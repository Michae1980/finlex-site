#!/usr/bin/env python3
"""
FinLex 静态交互原型构建与脱敏校验脚本（零第三方依赖，需 Python 3.9+）

功能：
1. 从关联项目 ../finlex/backend/data/finlex.db 读取规范文档、条文与关联边；
2. 执行对外隐私与合规红线校验（剥离内部备注/本机路径，校验官网 URL，标注用户补充案例）；
3. 按纯业务主题归并 4 级联级分类（问题域 -> 规范层级 -> 效力状态 -> 业务专题）；
4. 导出轻量首屏索引 prototype/data/index.js、按需全库正文检索引擎 prototype/data/fulltext.js
   以及按文档拆分的 prototype/data/docs/doc_<id>.js（兼容 file:// 双击离线直接打开无 CORS 限制）；
5. 同步生成 prototype/index.html（基于 prototype/template.html）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT.parent / "finlex" / "backend" / "data" / "finlex.db"
PROTOTYPE_DIR = PROJECT_ROOT / "prototype"
DATA_DIR = PROTOTYPE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
TEMPLATE_PATH = PROTOTYPE_DIR / "template.html"
OUTPUT_HTML = PROTOTYPE_DIR / "index.html"

# 隐私红线检测正则：禁止泄漏任何本机绝对路径
LOCAL_PATH_RE = re.compile(r"(/Users/[^\s\"'<>]+|[A-Za-z]:\\Users\\[^\s\"'<>]+)")

DOMAIN_META = [
    {"id": "accounting", "label": "会计准则与核算"},
    {"id": "tax", "label": "税收法规与征管"},
    {"id": "audit", "label": "审计准则与实务"},
    {"id": "general", "label": "综合商法与监管"},
]

DOC_TYPE_META = [
    {"id": "law", "label": "法律", "authority": 1},
    {"id": "regulation", "label": "行政法规", "authority": 2},
    {"id": "standard", "label": "准则", "authority": 3},
    {"id": "rule", "label": "部门规章", "authority": 4},
    {"id": "guidance", "label": "解释 / 指南 / 解答", "authority": 5},
    {"id": "normative", "label": "规范性文件与优惠", "authority": 6},
    {"id": "interpretation", "label": "官方解读", "authority": 7},
    {"id": "case", "label": "实务案例（参考）", "authority": 8},
]

STATUS_META = [
    {"id": "in_force", "label": "现行有效"},
    {"id": "will_replace", "label": "现行·即将替代"},
    {"id": "upcoming", "label": "尚未生效"},
    {"id": "outdated", "label": "非最新版"},
    {"id": "pending", "label": "占位待补"},
]

# 问题域权威权重（参考 finlex/docs/04-交叉联想设计.md，数值越小权威越高）
AUTHORITY_RANK = {
    ("accounting", "standard"): 1,
    ("accounting", "guidance"): 2,
    ("accounting", "law"): 3,
    ("accounting", "rule"): 4,
    ("accounting", "normative"): 5,
    ("accounting", "interpretation"): 6,
    ("accounting", "case"): 99,
    ("tax", "law"): 1,
    ("tax", "regulation"): 2,
    ("tax", "rule"): 3,
    ("tax", "normative"): 4,
    ("tax", "interpretation"): 5,
    ("tax", "case"): 99,
    ("audit", "standard"): 1,
    ("audit", "guidance"): 2,
    ("audit", "law"): 3,
    ("audit", "case"): 99,
    ("general", "law"): 1,
    ("general", "regulation"): 2,
    ("general", "rule"): 3,
    ("general", "normative"): 4,
    ("general", "case"): 99,
}

# 按纯业务主题归并（准则应用指南、审计问题解答均直接归入对应业务专题）
TOPIC_RULES = [
    ("case_ref", "实务案例（非规范参考）", lambda d: d["doc_type"] == "case"),
    # 会计域（纯业务主题）
    (
        "acc_rev_fin",
        "收入、金融工具与租赁",
        lambda d: d["domain"] == "accounting"
        and any(k in d["title"] for k in ("收入", "金融", "租赁", "套期", "公允价值", "股份支付", "保险")),
    ),
    (
        "acc_assets",
        "存货、固定资产与长期资产",
        lambda d: d["domain"] == "accounting"
        and any(
            k in d["title"]
            for k in ("存货", "固定资产", "无形资产", "投资性房地产", "资产减值", "生物资产", "石油", "非货币性", "借款费用", "持有待售")
        ),
    ),
    (
        "acc_liab_spec",
        "职工薪酬、补助、所得税与特殊交易",
        lambda d: d["domain"] == "accounting"
        and any(k in d["title"] for k in ("职工薪酬", "企业年金", "债务重组", "或有事项", "政府补助", "所得税", "外币")),
    ),
    (
        "acc_equity_report",
        "合并报表、股权投资与财务列报",
        lambda d: d["domain"] == "accounting"
        and any(
            k in d["title"]
            for k in (
                "基本准则",
                "合并",
                "长期股权",
                "财务报表",
                "现金流量",
                "中期",
                "分部",
                "关联方",
                "每股收益",
                "合营",
                "在其他主体",
                "资产负债表日后",
                "会计政策",
                "首次执行",
                "小企业会计准则",
                "可持续披露",
            )
        ),
    ),
    (
        "acc_comp_interp",
        "准则综合解释（第1–20号）与总指南",
        lambda d: d["domain"] == "accounting",
    ),
    # 税务域
    (
        "tax_income",
        "企业所得税与个人所得税",
        lambda d: d["domain"] == "tax" and any(k in d["title"] for k in ("所得税", "研发费用", "高新技术")),
    ),
    (
        "tax_vat_inv",
        "增值税与发票管理",
        lambda d: d["domain"] == "tax" and any(k in d["title"] for k in ("增值税", "发票", "出口退税", "小规模")),
    ),
    (
        "tax_admin",
        "税收征管与小微优惠",
        lambda d: d["domain"] == "tax",
    ),
    # 审计域（将审计准则与问题解答按纯审计业务循环归并）
    (
        "audit_ic_special",
        "内部控制与特殊行业/鉴证业务",
        lambda d: d["domain"] == "audit"
        and any(
            k in d["title"]
            for k in (
                "内部控制",
                "其他鉴证",
                "鉴证业务",
                "审阅准则",
                "相关服务",
                "特殊目的",
                "验资",
                "单一财务报表",
                "简要财务报表",
                "商业银行",
                "银行监管",
                "环境事项",
                "衍生金融",
                "电子商务",
            )
        ),
    ),
    (
        "audit_evidence",
        "审计证据、函证、存货与会计估计",
        lambda d: d["domain"] == "audit"
        and any(
            k in d["title"]
            for k in (
                "证据",
                "存货",
                "函证",
                "分析程序",
                "抽样",
                "会计估计",
                "关联方",
                "持续经营",
                "期初",
                "期后",
                "书面声明",
                "货币资金",
                "商誉减值",
                "收入确认",
                "信用损失",
            )
        ),
    ),
    (
        "audit_risk_fraud",
        "风险评估、重要性与舞弊应对",
        lambda d: d["domain"] == "audit"
        and any(
            k in d["title"]
            for k in (
                "舞弊",
                "计划审计",
                "重大错报风险",
                "重要性",
                "应对措施",
                "服务机构",
                "评价审计",
                "职业怀疑",
                "非常规交易",
                "会计分录",
                "法律法规",
            )
        ),
    ),
    (
        "audit_report_gov",
        "审计报告、集团审计与质量管理",
        lambda d: d["domain"] == "audit",
    ),
    # 综合法域
    (
        "general_corp",
        "会计法、公司法与综合商法",
        lambda d: d["domain"] == "general",
    ),
]


def classify_topic(doc: dict) -> tuple[str, str]:
    for tid, label, pred in TOPIC_RULES:
        if pred(doc):
            return tid, label
    return "general_corp", "其他综合规范"


def sanitize_url(raw_url: str | None) -> tuple[str | None, str]:
    if not raw_url:
        return None, "official_pending"
    val = raw_url.strip()
    if val.lower() == "user-submitted":
        return None, "user_submitted"
    if val.startswith("http://") or val.startswith("https://"):
        if "maoyanqing.com" in val.lower():
            return val, "third_party"
        return val, "official"
    return None, "official_pending"


def clean_text(text: str | None) -> tuple[str, int]:
    if not text:
        return "", 0
    hits = len(LOCAL_PATH_RE.findall(text))
    cleaned = LOCAL_PATH_RE.sub("[已脱敏路径]", text) if hits else text
    return cleaned.strip(), hits


def make_first_article_preview(articles: list[dict]) -> str:
    for a in articles:
        raw = (a["text"] or "").strip()
        if not raw:
            continue
        one_line = re.sub(r"\s+", " ", raw)
        prefix = f"{a['no']}：" if a["no"] and not one_line.startswith(a["no"]) else ""
        snippet = f"{prefix}{one_line}"
        return snippet[:108] + ("…" if len(snippet) > 108 else "")
    return ""


SERIES_PATTERNS = [
    (re.compile(r"^中国注册会计师审计准则问题解答第(\d+)号——(.+)$"), lambda m: (f"审计问答 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^中国注册会计师审计准则第(\d+)号——(.+)$"), lambda m: (f"审计准则 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^中国注册会计师其他鉴证业务准则第(\d+)号——(.+)$"), lambda m: (f"其他鉴证 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^中国注册会计师审阅准则第(\d+)号——(.+)$"), lambda m: (f"审阅准则 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^中国注册会计师相关服务准则第(\d+)号——(.+)$"), lambda m: (f"相关服务 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^企业会计准则第0*(\d+)号——(.+?)应用指南$"), lambda m: (f"会计指南 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^企业会计准则——(.+?)应用指南$"), lambda m: ("会计指南", m.group(1))),
    (re.compile(r"^企业会计准则第0*(\d+)号——(.+)$"), lambda m: (f"会计准则 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^企业会计准则——(.+)$"), lambda m: ("会计准则", m.group(1))),
    (re.compile(r"^企业会计准则解释第(\d+)号$"), lambda m: (f"准则解释 第{m.group(1)}号", f"企业会计准则解释第{m.group(1)}号")),
    (re.compile(r"^企业会计准则实施问答——(.+)$"), lambda m: ("实施问答", m.group(1))),
    (re.compile(r"^(.+?)实施问答$"), lambda m: ("实施问答", m.group(1))),
    (re.compile(r"^企业内部控制配套指引——(.+)$"), lambda m: ("内控配套指引", m.group(1))),
    (re.compile(r"^企业可持续披露准则第(\d+)号——(.+)$"), lambda m: (f"可持续披露 第{m.group(1)}号", m.group(2))),
    (re.compile(r"^发布通知——(.+)$"), lambda m: ("发布通知", m.group(1))),
    (re.compile(r"^中华人民共和国(.+)$"), lambda m: ("国家法律", m.group(1))),
]

TRAILING_PAREN_RE = re.compile(r"[（(]([^（）()]+)[）)]$")


def extract_display_parts(title: str, doc_type: str) -> tuple[str, str, str]:
    """拆解冗长法规全称为 (series_badge, display_title, revision_badge)，保留完整 title 供引用与正文区展示。"""
    base = title.strip()
    revision_badge = ""

    m_paren = TRAILING_PAREN_RE.search(base)
    if m_paren:
        inner = m_paren.group(1).strip()
        m_rev = re.search(r"(\d{4})年.*?(修订|修正|发布)", inner)
        if m_rev:
            revision_badge = f"{m_rev.group(1)}{m_rev.group(2)}"
            base = base[: m_paren.start()].strip()
        elif "财会〔" in inner:
            revision_badge = inner
            base = base[: m_paren.start()].strip()

    for pat, builder in SERIES_PATTERNS:
        m = pat.match(base)
        if m:
            series, short_title = builder(m)
            if series == "国家法律" and doc_type == "regulation":
                series = "行政法规"
            elif series == "国家法律" and doc_type == "rule":
                series = "部门规章"
            return series, short_title.strip(), revision_badge

    return "", base, revision_badge


def build_from_db(db_path: Path) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(f"未找到数据库文件：{db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    raw_docs = cur.execute(
        """
        SELECT id, doc_type, domain, title, doc_no, issuer, pub_date,
               effective_date, status, replaced_by_doc_id, parent_doc_id,
               source_name, source_url, source_date, summary
        FROM documents
        ORDER BY id ASC
        """
    ).fetchall()

    raw_articles = cur.execute(
        """
        SELECT id, document_id, article_no, heading, text_raw, seq
        FROM articles
        ORDER BY document_id ASC, seq ASC, id ASC
        """
    ).fetchall()

    link_cols = {r[1] for r in cur.execute("PRAGMA table_info(article_links)").fetchall()}
    score_expr = "COALESCE(l.score, 60)" if "score" in link_cols else "60"
    tier_expr = "COALESCE(l.tier, 'L3')" if "tier" in link_cols else "'L3'"
    raw_links = cur.execute(
        f"""
        SELECT l.id, l.from_article_id, l.to_article_id, l.link_type,
               l.note, l.strength, l.rel_kind,
               {score_expr} AS score, {tier_expr} AS tier,
               a1.document_id AS from_doc_id, a1.article_no AS from_art_no, a1.seq AS from_seq,
               a2.document_id AS to_doc_id, a2.article_no AS to_art_no, a2.seq AS to_seq
        FROM article_links l
        JOIN articles a1 ON l.from_article_id = a1.id
        JOIN articles a2 ON l.to_article_id = a2.id
        ORDER BY {score_expr} DESC, l.id ASC
        """
    ).fetchall()
    conn.close()

    privacy_redactions = 0
    articles_by_doc: dict[int, list[dict]] = defaultdict(list)
    fulltext_rows: list[list] = []

    for row in raw_articles:
        text_clean, hits = clean_text(row["text_raw"])
        heading_clean, h_hits = clean_text(row["heading"])
        privacy_redactions += hits + h_hits
        art_no = (row["article_no"] or "").strip()
        articles_by_doc[row["document_id"]].append(
            {
                "id": row["id"],
                "no": art_no,
                "heading": heading_clean,
                "text": text_clean,
                "seq": row["seq"],
            }
        )
        # 紧凑全库全文检索语料行：[doc_id, article_no, heading, text]
        compact_text = re.sub(r"\s+", " ", text_clean)
        fulltext_rows.append([row["document_id"], art_no, heading_clean, compact_text])

    # 预先建立文档查找表与企业会计准则最新版本年份映射（用于自动识别 2006 旧版应用指南冲突）
    raw_doc_map = {r["id"]: r for r in raw_docs}
    today_iso = dt.date.today().isoformat()
    cas_latest_std: dict[int, dict] = {}
    for r in raw_docs:
        if r["domain"] == "accounting" and r["doc_type"] == "standard" and "企业会计准则第" in (r["title"] or ""):
            m_num = re.search(r"第0*(\d+)号", r["title"])
            if m_num:
                num = int(m_num.group(1))
                dno_m = re.search(r"〔(\d{4})〕", r["doc_no"] or "")
                pub_y = (r["pub_date"] or "")[:4]
                eff_y = (r["effective_date"] or "")[:4]
                rev_y = dno_m.group(1) if dno_m else (pub_y if pub_y >= "2014" else eff_y)
                prev = cas_latest_std.get(num)
                if not prev or rev_y > prev["year"]:
                    cas_latest_std[num] = {
                        "year": rev_y,
                        "doc_no": (r["doc_no"] or "").strip(),
                        "title": (r["title"] or "").strip(),
                    }

    def detect_date_warning(r: sqlite3.Row) -> str:
        pdate = (r["pub_date"] or "").strip()
        edate = (r["effective_date"] or "").strip()
        dno = (r["doc_no"] or "").strip()
        if not pdate or not edate:
            return "发布或生效日期缺失，待核校（正文为现行版）"
        if pdate in ("2026-09-14", "2026-09-15"):
            return "发布日期疑似为批量入库日期，待核校（正文为现行版）"
        if ("2014" in dno and pdate < "2014") or ("2017" in dno and pdate < "2017") or (pdate == "2008-06-18" and edate >= "2014"):
            return "发布日期元数据与修订版次不符，待核校（正文已为修订版）"
        return ""

    documents: list[dict] = []
    doc_ids_set: set[int] = set()
    topic_labels: dict[str, str] = {}
    warnings: list[str] = []

    for row in raw_docs:
        doc_id = row["id"]
        doc_ids_set.add(doc_id)
        title, h1 = clean_text(row["title"])
        summary, h2 = clean_text(row["summary"])
        privacy_redactions += h1 + h2

        pub_date_str = (row["pub_date"] or "").strip()
        eff_date_str = (row["effective_date"] or "").strip()
        doc_no_str = (row["doc_no"] or "").strip()
        rep_id = row["replaced_by_doc_id"]
        rep_row = raw_doc_map.get(rep_id) if rep_id else None

        eff_status = row["status"] or "in_force"
        version_level = ""
        version_note = ""

        # 1. 占位总目录条目（无具体条文正文）
        if doc_id in (89, 90) or eff_status == "pending":
            eff_status = "pending"
            version_level = "stub"
            version_note = "占位说明：本条仅含收录/获取说明，不含具体应用指南条文"
        # 2. 尚未生效的已发布新版（effective_date > today）
        elif eff_date_str and eff_date_str > today_iso:
            eff_status = "upcoming"
            version_level = "upcoming"
            version_note = f"尚未生效：将于 {eff_date_str} 起施行，当前过渡期仍适用现行旧版"
        # 3. 已有替代新版（区分「新版尚未生效→现行·即将替代」与「新版已生效→非最新版」）
        elif rep_row is not None:
            rep_eff = (rep_row["effective_date"] or "").strip()
            rep_title = (rep_row["title"] or "").strip()
            if rep_eff and rep_eff > today_iso:
                eff_status = "will_replace"
                version_level = "will_replace"
                version_note = f"现行有效（即将替代）：已发布新版《{rep_title}》，将于 {rep_eff} 起施行"
            else:
                eff_status = "outdated"
                version_level = "conflict"
                version_note = f"非最新版：已被《{rep_title}》替代"
        # 4. 2006版企业会计准则分则应用指南（财会〔2006〕18号）核查
        elif row["domain"] == "accounting" and "应用指南" in title and "财会〔2006〕18号" in doc_no_str:
            eff_status = "outdated"
            m_num = re.search(r"第0*(\d+)号", title)
            std_info = cas_latest_std.get(int(m_num.group(1))) if m_num else None
            if std_info and std_info["year"] >= "2014":
                version_level = "conflict"
                dno_tag = f"（{std_info['doc_no']}）" if std_info["doc_no"] else ""
                version_note = f"非最新版（与新准则冲突）：本指南为2006旧版，对应准则已于{std_info['year']}年修订{dno_tag}，请以《应用指南汇编2024》及财政部实施问答为准"
            else:
                version_level = "stale"
                version_note = "非最新版：本指南为2006年版，财政部已出版《企业会计准则应用指南汇编2024》并吸收历年准则解释修订"
        # 5. 特殊修订动态提示（税收征管法修订草案已初审但2015版仍现行有效）
        elif doc_id == 76:
            eff_status = "in_force"
            version_level = "info"
            version_note = "2015版现行有效；修订草案已于2026年11月经全国人大常委会初审，尚未通过施行"

        date_warning = detect_date_warning(row)

        source_url, source_kind = sanitize_url(row["source_url"])
        arts = articles_by_doc.get(doc_id, [])
        first_preview = make_first_article_preview(arts)
        series_badge, display_title, revision_badge = extract_display_parts(title, row["doc_type"] or "normative")

        if row["doc_type"] == "case" and len(summary) < 20:
            warnings.append(f"案例 doc_id={doc_id} 摘要不足 20 字")

        doc_obj = {
            "id": doc_id,
            "domain": row["domain"] or "general",
            "doc_type": row["doc_type"] or "normative",
            "title": title,
            "display_title": display_title,
            "series_badge": series_badge,
            "revision_badge": revision_badge,
            "doc_no": doc_no_str or "待核实",
            "issuer": (row["issuer"] or "").strip() or "待核实",
            "pub_date": pub_date_str or "待核实",
            "effective_date": eff_date_str or "待核实",
            "status": eff_status,
            "version_level": version_level,
            "version_note": version_note,
            "date_warning": date_warning,
            "replaced_by_doc_id": rep_id,
            "source_name": (row["source_name"] or "").strip() or (row["issuer"] or "官方渠道"),
            "source_url": source_url,
            "source_kind": source_kind,
            "summary": summary,
            "first_preview": first_preview,
            "article_count": len(arts),
            "authority_rank": AUTHORITY_RANK.get((row["domain"], row["doc_type"]), 50),
            "is_case": row["doc_type"] == "case",
        }
        tid, tlabel = classify_topic(doc_obj)
        doc_obj["topic_id"] = tid
        doc_obj["topic_label"] = tlabel
        topic_labels[tid] = tlabel
        documents.append(doc_obj)

    # 聚合条文级关联边为文档级图谱边，保留五层分级、0-100 相关性分值与精确条文跳转索引
    strength_order = {"strong": 3, "medium": 2, "weak": 1}
    tier_order = {"L1": 5, "L2": 4, "L3": 3, "L4": 2, "L5": 1}
    edge_map: dict[tuple[int, int, str], dict] = {}
    dangling_links = 0

    for row in raw_links:
        fd = row["from_doc_id"]
        td = row["to_doc_id"]
        if fd not in doc_ids_set or td not in doc_ids_set:
            dangling_links += 1
            continue
        if fd == td:
            continue
        rel_kind = row["rel_kind"] or "cites"
        strength = row["strength"] or "medium"
        score = int(row["score"] or 60)
        tier = row["tier"] or "L3"
        note, h_note = clean_text(row["note"])
        privacy_redactions += h_note

        key = (fd, td, rel_kind)
        if key not in edge_map:
            edge_map[key] = {
                "id": f"e_{fd}_{td}_{rel_kind}",
                "from_doc_id": fd,
                "to_doc_id": td,
                "rel_kind": rel_kind,
                "strength": strength,
                "score": score,
                "tier": tier,
                "count": 0,
                "pairs": [],
            }
        edge = edge_map[key]
        if score > edge["score"]:
            edge["score"] = score
        if tier_order.get(tier, 0) > tier_order.get(edge["tier"], 0):
            edge["tier"] = tier
        if strength_order.get(strength, 0) > strength_order.get(edge["strength"], 0):
            edge["strength"] = strength
        edge["count"] += 1
        if len(edge["pairs"]) < 12:
            edge["pairs"].append(
                {
                    "from_art_no": (row["from_art_no"] or "").strip(),
                    "to_art_no": (row["to_art_no"] or "").strip(),
                    "from_seq": int(row["from_seq"] or 0),
                    "to_seq": int(row["to_seq"] or 0),
                    "score": score,
                    "strength": strength,
                    "note": note,
                }
            )

    # 补充 documents.replaced_by_doc_id 显式版本链
    for d in documents:
        rep_id = d["replaced_by_doc_id"]
        if rep_id and rep_id in doc_ids_set:
            key = (d["id"], rep_id, "superseded_by")
            if key not in edge_map:
                edge_map[key] = {
                    "id": f"e_{d['id']}_{rep_id}_superseded_by",
                    "from_doc_id": d["id"],
                    "to_doc_id": rep_id,
                    "rel_kind": "superseded_by",
                    "strength": "strong",
                    "score": 98,
                    "tier": "L1",
                    "count": 1,
                    "pairs": [{"from_art_no": "全文", "to_art_no": "全文", "from_seq": 0, "to_seq": 0, "score": 98, "strength": "strong", "note": "效力沿革：已被新版本替代"}],
                }

    doc_links = sorted(
        edge_map.values(),
        key=lambda e: (-e["score"], -e["count"], e["from_doc_id"], e["to_doc_id"]),
    )

    in_deg: Counter[int] = Counter()
    out_deg: Counter[int] = Counter()
    for e in doc_links:
        out_deg[e["from_doc_id"]] += 1
        in_deg[e["to_doc_id"]] += 1
    for d in documents:
        d["out_degree"] = out_deg[d["id"]]
        d["in_degree"] = in_deg[d["id"]]
        d["total_degree"] = out_deg[d["id"]] + in_deg[d["id"]]

    topics_list = [
        {"id": tid, "label": label}
        for tid, label, _ in TOPIC_RULES
        if tid in topic_labels
    ]

    index_payload = {
        "meta": {
            "built_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "document_count": len(documents),
            "article_count": sum(len(v) for v in articles_by_doc.values()),
            "raw_link_count": len(raw_links),
            "doc_link_count": len(doc_links),
            "connected_doc_count": sum(1 for d in documents if d["total_degree"] > 0),
        },
        "taxonomy": {
            "domains": DOMAIN_META,
            "doc_types": DOC_TYPE_META,
            "statuses": STATUS_META,
            "topics": topics_list,
        },
        "documents": documents,
        "doc_links": doc_links,
    }

    # 写出首屏索引、全库按需全文语料、按文档条文分片
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    index_js_path = DATA_DIR / "index.js"
    index_js_path.write_text(
        "window.FINLEX_INDEX = " + json.dumps(index_payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    fulltext_js_path = DATA_DIR / "fulltext.js"
    fulltext_js_path.write_text(
        "window.__finlexFulltextLoaded(" + json.dumps(fulltext_rows, ensure_ascii=False, separators=(",", ":")) + ");\n",
        encoding="utf-8",
    )

    for doc_id in doc_ids_set:
        doc_payload = {"id": doc_id, "articles": articles_by_doc.get(doc_id, [])}
        doc_js_path = DOCS_DIR / f"doc_{doc_id}.js"
        doc_js_path.write_text(
            f"window.__finlexDocLoaded({doc_id}," + json.dumps(doc_payload, ensure_ascii=False, separators=(",", ":")) + ");\n",
            encoding="utf-8",
        )

    if TEMPLATE_PATH.exists():
        OUTPUT_HTML.write_text(TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    topic_counts = Counter(d["topic_label"] for d in documents)
    return {
        "documents": len(documents),
        "articles": index_payload["meta"]["article_count"],
        "raw_links": len(raw_links),
        "doc_links": len(doc_links),
        "connected_docs": index_payload["meta"]["connected_doc_count"],
        "dangling_links": dangling_links,
        "privacy_redactions": privacy_redactions,
        "warnings": warnings,
        "index_js_kb": round(index_js_path.stat().st_size / 1024, 1),
        "fulltext_js_kb": round(fulltext_js_path.stat().st_size / 1024, 1),
        "topic_distribution": dict(topic_counts.most_common()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="从 finlex.db 构建脱敏静态交互原型")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="finlex.db 路径")
    args = parser.parse_args()

    stats = build_from_db(args.db)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if stats["dangling_links"] > 0:
        print(f"ERROR: 检测到 {stats['dangling_links']} 条悬空关联边", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
