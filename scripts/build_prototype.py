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
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"
PROTOTYPE_DIR = PROJECT_ROOT / "prototype"
DATA_DIR = PROTOTYPE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
FT_DIR = DATA_DIR / "ft"
FT_SHARD_MAX_BYTES = 1_200_000
TEMPLATE_PATH = PROTOTYPE_DIR / "template.html"
OUTPUT_HTML = PROTOTYPE_DIR / "index.html"

# 隐私红线检测正则：禁止泄漏任何本机绝对路径
LOCAL_PATH_RE = re.compile(r"(/Users/[^\s\"'<>]+|[A-Za-z]:\\Users\\[^\s\"'<>]+)")

FRAMEWORK_META = [
    {"id": "CN", "label": "中国准则与法规", "short": "中国准则"},
    {"id": "INTL", "label": "国际准则（IFRS）", "short": "国际准则"},
    {"id": "US", "label": "美国准则（US GAAP）", "short": "美国准则"},
]

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
    # 国际准则（ESMA 执法案例 / ISSB / IAASB / IESBA / OECD / IFRS Accounting）英文业务专题
    (
        "intl_acc_cases",
        "ESMA Enforcement Cases (Non-Authoritative)",
        lambda d: d.get("framework") == "INTL" and d["doc_type"] == "case",
    ),
    (
        "intl_acc_esg",
        "Sustainability Disclosure (ISSB)",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "accounting"
        and any(k in d["title"] for k in ("IFRS S1", "IFRS S2", "SASB", "Integrated Reporting")),
    ),
    (
        "intl_aud_qm_ethics",
        "Quality Management & Ethics (ISQM / IESBA)",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "audit"
        and any(k in d["title"] for k in ("ISQM", "IESBA", "Assurance Engagements")),
    ),
    (
        "intl_aud_isa",
        "International Standards on Auditing (ISA)",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "audit"
        and (d["title"].startswith("ISA ") or "ISA for LCE" in d["title"]),
    ),
    (
        "intl_aud_assurance",
        "Review, Assurance & Related Services (ISRE / ISAE / ISSA / ISRS)",
        lambda d: d.get("framework") == "INTL" and d["domain"] == "audit",
    ),
    (
        "intl_tax_oecd",
        "International Tax (OECD Pillar Two & Treaties)",
        lambda d: d.get("framework") == "INTL" and d["domain"] == "tax",
    ),
    (
        "intl_gen_gov",
        "Corporate Governance, Internal Control & AML",
        lambda d: d.get("framework") == "INTL" and d["domain"] == "general",
    ),
    # 美国准则（US GAAP — FASB ASC）英文业务专题
    (
        "us_acc_guides",
        "US GAAP Framework & Big4 Roadmaps",
        lambda d: d.get("framework") == "US"
        and d["domain"] == "accounting"
        and (d["doc_type"] == "interpretation" or d["doc_no"] in ("CON 8", "ASC 105")),
    ),
    (
        "us_acc_pres",
        "Presentation (ASC 200 Series)",
        lambda d: d.get("framework") == "US"
        and d["domain"] == "accounting"
        and bool(re.match(r"^ASC 2\d\d\b", d["doc_no"] or "")),
    ),
    (
        "us_acc_assets",
        "Assets, Credit Losses & Intangibles (ASC 300 Series)",
        lambda d: d.get("framework") == "US"
        and d["domain"] == "accounting"
        and bool(re.match(r"^ASC 3\d\d\b", d["doc_no"] or "")),
    ),
    (
        "us_acc_liab_eq",
        "Liabilities, Debt & Equity (ASC 400–500 Series)",
        lambda d: d.get("framework") == "US"
        and d["domain"] == "accounting"
        and bool(re.match(r"^ASC [45]\d\d\b", d["doc_no"] or "")),
    ),
    (
        "us_acc_rev_exp",
        "Revenue, Compensation & Income Taxes (ASC 600–700 Series)",
        lambda d: d.get("framework") == "US"
        and d["domain"] == "accounting"
        and bool(re.match(r"^ASC [67]\d\d\b", d["doc_no"] or "")),
    ),
    (
        "us_acc_broad",
        "Broad Transactions & Industry (ASC 800–900 Series)",
        lambda d: d.get("framework") == "US" and d["domain"] == "accounting",
    ),
    (
        "us_aud_pcaob",
        "PCAOB & AICPA Auditing Standards (US)",
        lambda d: d.get("framework") == "US" and d["domain"] == "audit",
    ),
    (
        "us_tax_irc",
        "US Federal Corporate & International Tax (IRC)",
        lambda d: d.get("framework") == "US" and d["domain"] == "tax",
    ),
    (
        "us_gen_sec_sox",
        "SEC Regulation, SOX & FCPA Compliance",
        lambda d: d.get("framework") == "US" and d["domain"] == "general",
    ),
    (
        "intl_acc_guides",
        "Agenda Decisions & Big4 Guides",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "accounting"
        and (d["doc_type"] == "interpretation" or "Agenda Decisions" in d["title"] or "Practice Statement" in d["title"]),
    ),
    (
        "intl_acc_rev_fin",
        "Revenue, Financial Instruments & Leases",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "accounting"
        and any(
            k in d["title"]
            for k in ("Revenue", "Financial Instruments", "Lease", "Fair Value", "Insurance", "Share-based", "Construction Contracts", "Customer Loyalty", "Embedded Derivatives", "Extinguishing Financial")
        ),
    ),
    (
        "intl_acc_assets",
        "Inventories, PPE & Non-current Assets",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "accounting"
        and any(
            k in d["title"]
            for k in ("Inventories", "Property, Plant", "Intangible", "Investment Property", "Impairment", "Agriculture", "Mineral Resources", "Held for Sale", "Borrowing Costs", "Decommissioning", "Stripping Costs")
        ),
    ),
    (
        "intl_acc_liab_tax",
        "Taxes, Employee Benefits & Provisions",
        lambda d: d.get("framework") == "INTL"
        and d["domain"] == "accounting"
        and any(
            k in d["title"]
            for k in ("Income Tax", "Employee Benefits", "Retirement Benefit", "Government Grant", "Government Assistance", "Foreign Exchange", "Foreign Currency", "Hyperinflation", "Provisions", "Levies", "Regulatory", "Euro", "Waste Electrical", "Foreign Operation")
        ),
    ),
    (
        "intl_acc_group_pres",
        "Framework, Presentation & Group Reporting",
        lambda d: d.get("framework") == "INTL" and d["domain"] == "accounting",
    ),
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


def build_from_db(db_path: Path, *, include_private: bool = False, out_root: Path | None = None) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(f"未找到数据库文件：{db_path}")
    target_root = out_root if out_root is not None else PROTOTYPE_DIR
    out_data_dir = target_root / "data"
    out_docs_dir = out_data_dir / "docs"
    out_ft_dir = out_data_dir / "ft"
    out_html_path = target_root / "index.html"

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
            "framework": "CN",
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

    # 合并仓库内国际准则公开合规数据源（intl_data/*.json），ID 从 10001 起避免与 finlex.db 冲突
    intl_extra_edges: list[dict] = []
    if INTL_DATA_DIR.exists():
        cn_id_by_title = {d["title"]: d["id"] for d in documents if d["framework"] == "CN"}
        cn_cas_by_num: dict[int, int] = {}
        for d in documents:
            if d["framework"] == "CN" and d["domain"] == "accounting" and d["doc_type"] == "standard":
                m_cn = re.search(r"企业会计准则第0*(\d+)号", d["title"])
                if m_cn:
                    num = int(m_cn.group(1))
                    if num not in cn_cas_by_num or d["status"] == "in_force":
                        cn_cas_by_num[num] = d["id"]

        cn_docs_all = [d for d in documents if d["framework"] == "CN"]

        def resolve_cn_cas_id(target_title: str) -> int | None:
            if target_title in cn_id_by_title:
                return cn_id_by_title[target_title]
            m_t = re.search(r"企业会计准则第0*(\d+)号", target_title)
            if m_t:
                return cn_cas_by_num.get(int(m_t.group(1)))
            for d in cn_docs_all:
                if d["title"].startswith(target_title):
                    return d["id"]
            return None
        intl_raw_items: list[dict] = []
        for jf in sorted(INTL_DATA_DIR.glob("*.json")):
            payload_in = json.loads(jf.read_text(encoding="utf-8"))
            intl_raw_items.extend(payload_in.get("documents", []))

        # 方案 B：仅当显式传入 include_private=True 时，叠加本机 git-ignored 的 intl_data/private/*.json 官方段落全文
        private_overlay: dict[str, list[dict]] = {}
        private_overlay_base: dict[str, list[dict]] = {}
        private_dir = INTL_DATA_DIR / "private"
        if include_private and private_dir.exists():
            def _norm_base_code(c: str) -> str:
                return re.sub(r"\s*\(revised[^)]*\)", "", c, flags=re.IGNORECASE).strip().upper()
            for pjf in sorted(private_dir.glob("*.json")):
                pp = json.loads(pjf.read_text(encoding="utf-8"))
                pcode = (pp.get("code") or "").strip()
                if pcode and pp.get("articles"):
                    private_overlay[pcode] = pp["articles"]
                    private_overlay_base[_norm_base_code(pcode)] = pp["articles"]
            for item in intl_raw_items:
                icode = item.get("code", "")
                p_arts = private_overlay.get(icode) or private_overlay_base.get(_norm_base_code(icode))
                if p_arts:
                    base_arts = item.get("articles", [])
                    ov = [a for a in base_arts if a.get("no") == "Overview"]
                    rest = [a for a in base_arts if a.get("no") != "Overview"]
                    merged_p = ov + p_arts + rest
                    for idx_p, a_p in enumerate(merged_p):
                        a_p["seq"] = idx_p
                    item["articles"] = merged_p

        next_intl_doc_id = 10001
        next_intl_art_id = 1_000_001
        code_to_doc_id: dict[str, int] = {}
        staged_intl: list[tuple[int, dict]] = []
        for item in intl_raw_items:
            did = next_intl_doc_id
            next_intl_doc_id += 1
            code_to_doc_id[item.get("code", "")] = did
            staged_intl.append((did, item))

        for did, item in staged_intl:
            doc_ids_set.add(did)
            arts_out: list[dict] = []
            for a in item.get("articles", []):
                txt_clean, h_a = clean_text(a.get("text", ""))
                hd_clean, h_h = clean_text(a.get("heading", ""))
                privacy_redactions += h_a + h_h
                art_no = (a.get("no") or "").strip()
                arts_out.append(
                    {
                        "id": next_intl_art_id,
                        "no": art_no,
                        "heading": hd_clean,
                        "text": txt_clean,
                        "seq": int(a.get("seq", 0)),
                    }
                )
                next_intl_art_id += 1
                fulltext_rows.append([did, art_no, hd_clean, re.sub(r"\s+", " ", txt_clean)])
            articles_by_doc[did] = arts_out

            rep_code = (item.get("replaced_by_code") or "").strip()
            rep_did = code_to_doc_id.get(rep_code) if rep_code else None
            fw = item.get("framework") or "INTL"
            dom = item.get("domain") or "accounting"
            dtype = item.get("doc_type") or "standard"
            title_clean, h1 = clean_text(item.get("title", ""))
            sum_clean, h2 = clean_text(item.get("summary", ""))
            privacy_redactions += h1 + h2
            src_url, src_kind = sanitize_url(item.get("source_url"))
            if item.get("source_kind") in ("official", "third_party"):
                src_kind = item["source_kind"]

            doc_obj = {
                "id": did,
                "framework": fw,
                "domain": dom,
                "doc_type": dtype,
                "title": title_clean,
                "display_title": item.get("display_title") or title_clean,
                "series_badge": item.get("series_badge") or item.get("code", ""),
                "revision_badge": "",
                "doc_no": item.get("doc_no") or item.get("code", "待核实"),
                "issuer": item.get("issuer") or "IFRS Foundation",
                "pub_date": item.get("pub_date") or "2026-01-01",
                "effective_date": item.get("effective_date") or "2026-01-01",
                "status": item.get("status") or "in_force",
                "version_level": item.get("version_level") or "",
                "version_note": item.get("version_note") or "",
                "date_warning": "",
                "replaced_by_doc_id": rep_did,
                "source_name": item.get("source_name") or "IFRS Foundation",
                "source_url": src_url,
                "source_kind": src_kind,
                "summary": sum_clean,
                "first_preview": make_first_article_preview(arts_out),
                "article_count": len(arts_out),
                "authority_rank": AUTHORITY_RANK.get((dom, dtype), 50),
                "is_case": dtype == "case",
            }
            tid, tlabel = classify_topic(doc_obj)
            doc_obj["topic_id"] = tid
            doc_obj["topic_label"] = tlabel
            topic_labels[tid] = tlabel
            documents.append(doc_obj)

            # 1) 国际准则内部引用边（实务案例归 L5 applies_to，Big4 指南归 L5 explains，IFRIC 议程决议归 L2 amends，其余归 L3 cites）
            src_code = item.get("code", "")
            for cited_code in item.get("cited_codes", []):
                tdid = code_to_doc_id.get(cited_code)
                if tdid and tdid != did:
                    if dtype == "case":
                        rk_i, st_i, sc_i, tr_i = "applies_to", "weak", 40, "L5"
                        nt_i = f"ESMA enforcement case applying {cited_code} (reference only)"
                    elif dtype == "interpretation" or src_code.startswith("Big4 Guide"):
                        rk_i, st_i, sc_i, tr_i = "explains", "weak", 42, "L5"
                        nt_i = f"Big Four practical guide covering {cited_code}"
                    elif src_code == "IFRIC Agenda Decisions":
                        rk_i, st_i, sc_i, tr_i = "amends", "strong", 80, "L2"
                        nt_i = f"IFRIC Agenda Decisions interpreting {cited_code}"
                    else:
                        rk_i, st_i, sc_i, tr_i = "cites", "medium", 65, "L3"
                        nt_i = f"IFRS cross-reference: {src_code} -> {cited_code}"
                    intl_extra_edges.append(
                        {
                            "from_doc_id": did,
                            "to_doc_id": tdid,
                            "rel_kind": rk_i,
                            "strength": st_i,
                            "score": sc_i,
                            "tier": tr_i,
                            "note": nt_i,
                        }
                    )
            # 2) 跨体系对照边：中国 CAS <-> 国际 IFRS / US GAAP（rel_kind=intl_mapping）
            cas_pairs = list(item.get("cas_links", []))
            if src_code == "IAS 26" and not cas_pairs:
                cas_pairs = [("企业会计准则第10号——企业年金基金", "退休福利计划/企业年金基金对照")]
            for cas_title, note_txt in cas_pairs:
                cas_id = resolve_cn_cas_id(cas_title)
                if cas_id:
                    intl_extra_edges.append(
                        {
                            "from_doc_id": did,
                            "to_doc_id": cas_id,
                            "rel_kind": "intl_mapping",
                            "strength": "strong",
                            "score": 68,
                            "tier": "L4",
                            "note": f"中外准则对照：{note_txt}",
                        }
                    )
            for ifrs_code, note_txt in item.get("ifrs_links", []):
                ifrs_did = code_to_doc_id.get(ifrs_code)
                if ifrs_did and ifrs_did != did:
                    intl_extra_edges.append(
                        {
                            "from_doc_id": did,
                            "to_doc_id": ifrs_did,
                            "rel_kind": "intl_mapping",
                            "strength": "strong",
                            "score": 70,
                            "tier": "L4",
                            "note": f"美欧准则对照：{note_txt}",
                        }
                    )

        # 3) 国际准则结构化内部关联：核心家族配套（L1 companion）与 IFRIC/SIC 官方解释归属（L2 amends）
        intl_curated_links = [
            # L1 核心家族配套：金融工具套件、集团合并套件、财务报表列报与实务公告套件
            ("IFRS 7", "IFRS 9", "companion", "strong", 92, "L1", "Financial Instruments suite: disclosures companion to IFRS 9"),
            ("IAS 32", "IFRS 9", "companion", "strong", 92, "L1", "Financial Instruments suite: presentation companion to IFRS 9"),
            ("IAS 39", "IFRS 9", "companion", "strong", 90, "L1", "Financial Instruments suite: macro hedge accounting carve-out alongside IFRS 9"),
            ("IFRS 7", "IAS 32", "companion", "strong", 90, "L1", "Financial Instruments suite: disclosures & presentation companion"),
            ("IFRS 11", "IFRS 10", "companion", "strong", 92, "L1", "Group Reporting suite: joint arrangements companion to consolidation"),
            ("IFRS 12", "IFRS 10", "companion", "strong", 92, "L1", "Group Reporting suite: disclosures of interests in subsidiaries"),
            ("IFRS 12", "IFRS 11", "companion", "strong", 90, "L1", "Group Reporting suite: disclosures of interests in joint arrangements"),
            ("IFRS 12", "IAS 28", "companion", "strong", 90, "L1", "Group Reporting suite: disclosures of interests in associates & JVs"),
            ("IAS 27", "IFRS 10", "companion", "strong", 92, "L1", "Group Reporting suite: separate vs. consolidated financial statements"),
            ("IAS 28", "IFRS 10", "companion", "strong", 92, "L1", "Group Reporting suite: equity method companion to consolidation"),
            ("IFRS 3", "IFRS 10", "companion", "strong", 90, "L1", "Group Reporting suite: business combinations & consolidation"),
            ("IAS 8", "IFRS 18", "companion", "strong", 92, "L1", "Presentation suite: Basis of Preparation companion to IFRS 18"),
            ("IAS 7", "IFRS 18", "companion", "strong", 90, "L1", "Presentation suite: Statement of Cash Flows aligned with IFRS 18"),
            ("IFRS 19", "IFRS 18", "companion", "strong", 90, "L1", "Reduced disclosure framework for eligible subsidiaries under IFRS"),
            ("IFRS 19", "IFRS for SMEs", "companion", "strong", 88, "L1", "Simplified disclosure standards comparison (eligible subsidiaries vs. SMEs)"),
            ("IFRS for SMEs", "Conceptual Framework", "companion", "strong", 88, "L1", "Standalone SME standard grounded in the Conceptual Framework"),
            ("Preface", "Conceptual Framework", "companion", "strong", 90, "L1", "Foundational scope & objectives of IFRS Accounting Standards"),
            ("IAS 26", "IAS 19", "companion", "strong", 88, "L1", "Retirement benefit plans reporting companion to employee benefits"),
            ("Practice Statement 1", "IFRS 18", "companion", "strong", 88, "L1", "Management Commentary non-mandatory guidance complementing financial statements"),
            ("Practice Statement 1", "IAS 1", "companion", "strong", 86, "L1", "Management Commentary guidance alongside IAS 1 presentation"),
            ("Practice Statement 2", "IFRS 18", "companion", "strong", 88, "L1", "Making Materiality Judgements guidance for IFRS 18 disclosures"),
            ("Practice Statement 2", "IAS 1", "companion", "strong", 88, "L1", "Making Materiality Judgements guidance for IAS 1"),
            ("Practice Statement 2", "IAS 8", "companion", "strong", 86, "L1", "Materiality judgements in accounting policy & estimate disclosures"),
            # L2 IFRIC / SIC 现行官方解释归属母准则
            ("IFRIC 1", "IAS 16", "amends", "strong", 84, "L2", "IFRIC interpretation of decommissioning changes in PPE cost"),
            ("IFRIC 1", "IAS 37", "amends", "strong", 84, "L2", "IFRIC interpretation of decommissioning & restoration provisions"),
            ("IFRIC 2", "IAS 32", "amends", "strong", 84, "L2", "IFRIC interpretation of co-operative shares liability vs. equity"),
            ("IFRIC 5", "IAS 37", "amends", "strong", 84, "L2", "IFRIC interpretation of decommissioning rehabilitation funds"),
            ("IFRIC 6", "IAS 37", "amends", "strong", 84, "L2", "IFRIC interpretation of WEEE waste-management liabilities"),
            ("IFRIC 7", "IAS 29", "amends", "strong", 84, "L2", "IFRIC interpretation of hyperinflation restatement approach"),
            ("IFRIC 10", "IAS 34", "amends", "strong", 84, "L2", "IFRIC interpretation of interim reporting & impairment"),
            ("IFRIC 10", "IAS 36", "amends", "strong", 84, "L2", "IFRIC interpretation prohibiting goodwill impairment reversal after interim period"),
            ("IFRIC 12", "IFRS 15", "amends", "strong", 84, "L2", "IFRIC interpretation of service concession revenue recognition"),
            ("IFRIC 12", "IAS 38", "amends", "strong", 84, "L2", "IFRIC interpretation of intangible asset model in service concessions"),
            ("IFRIC 12", "IFRS 9", "amends", "strong", 82, "L2", "IFRIC interpretation of financial asset model in service concessions"),
            ("IFRIC 14", "IAS 19", "amends", "strong", 84, "L2", "IFRIC interpretation of defined benefit asset ceiling & minimum funding"),
            ("IFRIC 16", "IAS 21", "amends", "strong", 84, "L2", "IFRIC interpretation of net investment hedges in foreign operations"),
            ("IFRIC 16", "IFRS 9", "amends", "strong", 84, "L2", "IFRIC interpretation of hedge accounting for net investments"),
            ("IFRIC 17", "IAS 10", "amends", "strong", 84, "L2", "IFRIC interpretation of non-cash dividend distributions to owners"),
            ("IFRIC 17", "IFRS 5", "amends", "strong", 82, "L2", "IFRIC interpretation of assets held for distribution to owners"),
            ("IFRIC 19", "IFRS 9", "amends", "strong", 84, "L2", "IFRIC interpretation of extinguishing financial liabilities with equity"),
            ("IFRIC 19", "IAS 32", "amends", "strong", 84, "L2", "IFRIC interpretation of equity instruments issued to extinguish debt"),
            ("IFRIC 20", "IAS 16", "amends", "strong", 84, "L2", "IFRIC interpretation of surface mine stripping costs"),
            ("IFRIC 21", "IAS 37", "amends", "strong", 84, "L2", "IFRIC interpretation of obligating events for government levies"),
            ("IFRIC 22", "IAS 21", "amends", "strong", 84, "L2", "IFRIC interpretation of exchange rate for advance consideration"),
            ("IFRIC 23", "IAS 12", "amends", "strong", 84, "L2", "IFRIC interpretation of uncertain income tax treatments"),
            ("SIC-7", "IAS 21", "amends", "strong", 82, "L2", "SIC interpretation of Euro introduction under IAS 21"),
            ("SIC-10", "IAS 20", "amends", "strong", 82, "L2", "SIC interpretation of government assistance without operating relation"),
            ("SIC-25", "IAS 12", "amends", "strong", 82, "L2", "SIC interpretation of tax status changes under IAS 12"),
            ("SIC-29", "IFRIC 12", "amends", "strong", 84, "L2", "SIC disclosure companion to IFRIC 12 Service Concession Arrangements"),
            ("SIC-32", "IAS 38", "amends", "strong", 82, "L2", "SIC interpretation of website development costs under IAS 38"),
            ("IFRIC Agenda Decisions", "IFRS 15", "amends", "strong", 80, "L2", "IFRIC Agenda Decisions addressing principal vs. agent & revenue recognition"),
            ("IFRIC Agenda Decisions", "IFRS 16", "amends", "strong", 80, "L2", "IFRIC Agenda Decisions addressing lease term & definition of a lease"),
            ("IFRIC Agenda Decisions", "IFRS 9", "amends", "strong", 80, "L2", "IFRIC Agenda Decisions addressing financial instruments & ECL"),
            ("IFRIC Agenda Decisions", "IAS 36", "amends", "strong", 80, "L2", "IFRIC Agenda Decisions addressing impairment testing"),
            ("IFRIC Agenda Decisions", "IAS 38", "amends", "strong", 80, "L2", "IFRIC Agenda Decisions addressing cloud computing & intangible assets"),
            # ISSB 可持续披露、IAASB 国际审计与鉴证、IESBA 道德守则、OECD 国际税收内部核心关联
            ("IFRS S2", "IFRS S1", "companion", "strong", 94, "L1", "ISSB core suite: IFRS S2 climate disclosures applied together with IFRS S1"),
            ("IFRS S2 Industry Guidance", "IFRS S2", "companion", "strong", 90, "L1", "Industry-based implementation metrics accompanying IFRS S2"),
            ("SASB Standards", "IFRS S1", "companion", "strong", 88, "L1", "Required source of industry guidance referenced by IFRS S1"),
            ("Integrated Reporting Framework", "IFRS S1", "companion", "strong", 86, "L1", "Connected financial & sustainability reporting framework"),
            ("ISSA 5000", "IFRS S1", "cross_domain", "strong", 72, "L4", "Sustainability assurance standard for IFRS S1/S2 disclosures"),
            ("ISSA 5000", "IFRS S2", "cross_domain", "strong", 72, "L4", "Sustainability assurance standard for IFRS S2 climate disclosures"),
            ("IESBA Code Part 5 (IESSA)", "ISSA 5000", "companion", "strong", 92, "L1", "Ethics & independence companion to ISSA 5000 sustainability assurance"),
            ("ISQM 2", "ISQM 1", "companion", "strong", 92, "L1", "Quality Management suite: Engagement Quality Reviews companion to ISQM 1"),
            ("ISA 220 (Revised)", "ISQM 1", "companion", "strong", 92, "L1", "Engagement-level quality management aligned with firm-level ISQM 1"),
            ("ISA 220 (Revised)", "ISQM 2", "companion", "strong", 90, "L1", "Engagement partner responsibilities interacting with EQR under ISQM 2"),
            ("ISA 330", "ISA 315 (Revised 2019)", "companion", "strong", 92, "L1", "Core audit risk model: responses to assessed risks under ISA 315"),
            ("ISA 240 (Revised)", "ISA 315 (Revised 2019)", "companion", "strong", 90, "L1", "Fraud risk assessment integrated with ISA 315"),
            ("ISA 540 (Revised)", "ISA 315 (Revised 2019)", "companion", "strong", 88, "L1", "Risk-based auditing of accounting estimates"),
            ("ISA 501", "ISA 500", "companion", "strong", 88, "L1", "Specific audit evidence considerations under ISA 500"),
            ("ISA 505", "ISA 500", "companion", "strong", 88, "L1", "External confirmations as audit evidence under ISA 500"),
            ("ISA 701", "ISA 700 (Revised)", "companion", "strong", 92, "L1", "Reporting suite: Key Audit Matters companion to ISA 700"),
            ("ISA 705 (Revised)", "ISA 700 (Revised)", "companion", "strong", 92, "L1", "Reporting suite: Modifications to the opinion companion to ISA 700"),
            ("ISA 706 (Revised)", "ISA 700 (Revised)", "companion", "strong", 90, "L1", "Reporting suite: Emphasis/Other Matter paragraphs companion to ISA 700"),
            ("ISA 720 (Revised)", "ISA 700 (Revised)", "companion", "strong", 88, "L1", "Reporting suite: Other information responsibilities alongside ISA 700"),
            ("ISA 800 (Revised)", "ISA 700 (Revised)", "companion", "strong", 86, "L1", "Special purpose framework audits built on ISA 700"),
            ("ISA 805 (Revised)", "ISA 700 (Revised)", "companion", "strong", 86, "L1", "Single financial statement audits built on ISA 700"),
            ("ISA 810 (Revised)", "ISA 700 (Revised)", "companion", "strong", 86, "L1", "Summary financial statement reporting built on ISA 700"),
            ("ISA for LCE", "ISA 200", "companion", "strong", 88, "L1", "Standalone proportionate audit standard for Less Complex Entities"),
            ("ISRE 2410", "ISRE 2400 (Revised)", "companion", "strong", 88, "L1", "Review engagements suite: interim review vs. general review"),
            ("ISAE 3400", "ISAE 3000 (Revised)", "companion", "strong", 88, "L1", "Prospective financial information assurance under ISAE 3000"),
            ("ISAE 3402", "ISAE 3000 (Revised)", "companion", "strong", 88, "L1", "Service organization controls assurance under ISAE 3000"),
            ("ISAE 3410", "ISAE 3000 (Revised)", "companion", "strong", 88, "L1", "GHG statement assurance under ISAE 3000"),
            ("ISAE 3420", "ISAE 3000 (Revised)", "companion", "strong", 88, "L1", "Pro forma financial information assurance under ISAE 3000"),
            ("IESBA Code Part 4A", "IESBA Code Part 1–3", "companion", "strong", 92, "L1", "Audit & review independence standards grounded in Parts 1–3"),
            ("IESBA Code Part 4B", "IESBA Code Part 1–3", "companion", "strong", 90, "L1", "Other assurance independence standards grounded in Parts 1–3"),
            ("IESBA Code Part 5 (IESSA)", "IESBA Code Part 1–3", "companion", "strong", 90, "L1", "Sustainability assurance ethics & independence (Volume 2)"),
            ("OECD Pillar Two (GloBE)", "IAS 12", "cross_domain", "strong", 74, "L4", "Pillar Two 15% global minimum tax directly linked to IAS 12 deferred tax exception & disclosures"),
            ("OECD Transfer Pricing Guidelines", "OECD Model Tax Convention", "companion", "strong", 90, "L1", "Arm's length principle & transfer pricing companion to Article 9 of Model Tax Convention"),
            ("COSO ERM (2017)", "COSO Internal Control (ICIF)", "companion", "strong", 90, "L1", "COSO governance suite: Enterprise Risk Management complementing Internal Control (ICIF)"),
            ("COSO Internal Control (ICIF)", "ISA 315 (Revised 2019)", "cross_domain", "strong", 74, "L4", "COSO 5-component internal control framework directly aligned with ISA 315 control evaluation"),
            ("G20/OECD Corporate Governance", "IFRS S1", "cross_domain", "strong", 72, "L4", "Chapter VI sustainability governance & resilience interoperable with IFRS S1"),
            ("OECD MNE Guidelines (RBC)", "G20/OECD Corporate Governance", "companion", "strong", 88, "L1", "OECD corporate governance & responsible business conduct companion standards"),
            ("FATF 40 Recommendations", "ISA 250 (Revised)", "cross_domain", "strong", 72, "L4", "FATF AML/CFT/DNFBP obligations interacting with auditor NOCLAR responsibilities"),
            # US GAAP (FASB ASC) 核心家族配套（L1 companion）
            ("ASC 105", "CON 8", "companion", "strong", 90, "L1", "Foundational US GAAP hierarchy & FASB Conceptual Framework"),
            ("ASC 210", "ASC 205", "companion", "strong", 90, "L1", "US GAAP Presentation suite: Balance Sheet companion to ASC 205"),
            ("ASC 220", "ASC 205", "companion", "strong", 90, "L1", "US GAAP Presentation suite: Income Statement & OCI companion to ASC 205"),
            ("ASC 230", "ASC 205", "companion", "strong", 90, "L1", "US GAAP Presentation suite: Statement of Cash Flows companion to ASC 205"),
            ("ASC 321", "ASC 320", "companion", "strong", 90, "L1", "US GAAP Financial Instruments suite: Equity vs. Debt securities"),
            ("ASC 326", "ASC 320", "companion", "strong", 92, "L1", "US GAAP Financial Instruments suite: CECL credit losses companion to debt & receivables"),
            ("ASC 815", "ASC 320", "companion", "strong", 90, "L1", "US GAAP Financial Instruments suite: Derivatives & hedging"),
            ("ASC 825", "ASC 320", "companion", "strong", 90, "L1", "US GAAP Financial Instruments suite: Fair Value Option & disclosures"),
            ("ASC 340", "ASC 606", "companion", "strong", 92, "L1", "US GAAP Revenue suite: Contract costs (ASC 340-40) companion to ASC 606"),
            ("ASC 610", "ASC 606", "companion", "strong", 90, "L1", "US GAAP Revenue suite: Nonfinancial asset derecognition companion to ASC 606"),
            ("ASC 350", "ASC 360", "companion", "strong", 90, "L1", "US GAAP Long-Lived Assets suite: Goodwill/Intangibles & PP&E impairment"),
            ("ASC 730", "ASC 350", "companion", "strong", 90, "L1", "US GAAP R&D expensing vs. capitalized intangibles/software"),
            ("ASC 985", "ASC 350", "companion", "strong", 90, "L1", "US GAAP Software suite: external-sale software (985-20) vs. internal-use (350-40)"),
            ("ASC 805", "ASC 810", "companion", "strong", 92, "L1", "US GAAP Group Reporting suite: Business Combinations & Consolidation"),
            ("ASC 323", "ASC 810", "companion", "strong", 90, "L1", "US GAAP Group Reporting suite: Equity Method & Consolidation"),
            ("ASC 480", "ASC 470", "companion", "strong", 90, "L1", "US GAAP Debt & Equity suite: Liabilities vs. Equity & Convertible Debt"),
            ("ASC 405", "ASC 470", "companion", "strong", 88, "L1", "US GAAP Liabilities suite: Extinguishments & Debt modifications"),
            # US Audit (PCAOB), US Tax (IRC) & US Securities/SOX 核心家族配套（L1 companion / L4 cross_domain）
            ("PCAOB QC 1000", "PCAOB AS 1000", "companion", "strong", 92, "L1", "PCAOB Quality Control suite: Firm QC system companion to AS 1000"),
            ("PCAOB AS 1220", "PCAOB QC 1000", "companion", "strong", 90, "L1", "PCAOB Quality Control suite: Engagement Quality Review companion to QC 1000"),
            ("PCAOB AS 2301", "PCAOB AS 2110", "companion", "strong", 92, "L1", "PCAOB Risk Model: Responses to assessed risks under AS 2110"),
            ("PCAOB AS 2201", "SOX (2002)", "cross_domain", "strong", 76, "L4", "SOX Section 404(b) statutory mandate implemented via PCAOB AS 2201 ICFR integrated audit"),
            ("PCAOB AS 3101", "PCAOB AS 1301", "companion", "strong", 90, "L1", "PCAOB Reporting suite: Critical Audit Matters (CAMs) drawn from Audit Committee communications"),
            ("IRC §951 / §951A", "IRC §11 & §55 (CAMT)", "companion", "strong", 90, "L1", "US Corporate & International Tax suite: CFC Subpart F/GILTI alongside §11 corporate tax"),
            ("IRC §59A (BEAT)", "IRC §11 & §55 (CAMT)", "companion", "strong", 90, "L1", "US Corporate Tax suite: Base Erosion & Anti-Abuse Tax backstop to §11"),
            ("IRC §163(j)", "IRC §11 & §55 (CAMT)", "companion", "strong", 88, "L1", "US Corporate Tax suite: Business interest deduction limitation under Title 26"),
            ("SEC Regulation S-X", "Securities Acts (1933 / 1934)", "companion", "strong", 92, "L1", "SEC Reporting suite: Financial statement form & auditor independence rules"),
            ("SEC Regulation S-K", "Securities Acts (1933 / 1934)", "companion", "strong", 92, "L1", "SEC Reporting suite: MD&A, Non-GAAP & cybersecurity disclosure rules"),
            ("FCPA (1977)", "Securities Acts (1933 / 1934)", "companion", "strong", 88, "L1", "Exchange Act §13(b)(2) books-and-records & anti-bribery enforcement"),
        ]
        for fc, tc, rk_c, st_c, sc_c, tr_c, nt_c in intl_curated_links:
            fd_c = code_to_doc_id.get(fc)
            td_c = code_to_doc_id.get(tc)
            if fd_c and td_c and fd_c != td_c:
                intl_extra_edges.append(
                    {
                        "from_doc_id": fd_c,
                        "to_doc_id": td_c,
                        "rel_kind": rk_c,
                        "strength": st_c,
                        "score": sc_c,
                        "tier": tr_c,
                        "note": nt_c,
                    }
                )

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
        # 首屏 index.js 每条文档边仅保留 Top 4 代表性条文明细（完整条对条已嵌入 doc_<id>.js）
        if len(edge["pairs"]) < 4:
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

    # 合并国际准则内部引用与 CAS<->IFRS 趋同对照边（同一文档对优先保留高优先级 L1/L2/L5 语义边，避免与普通 L3 cites 重复）
    intl_best_pair: dict[tuple[int, int], dict] = {}
    for ie in intl_extra_edges:
        fd, td = ie["from_doc_id"], ie["to_doc_id"]
        if fd not in doc_ids_set or td not in doc_ids_set or fd == td:
            continue
        prev = intl_best_pair.get((fd, td))
        if not prev or ie["score"] > prev["score"]:
            intl_best_pair[(fd, td)] = ie
    for ie in intl_best_pair.values():
        fd, td, rk = ie["from_doc_id"], ie["to_doc_id"], ie["rel_kind"]
        key = (fd, td, rk)
        if key not in edge_map:
            edge_map[key] = {
                "id": f"e_{fd}_{td}_{rk}",
                "from_doc_id": fd,
                "to_doc_id": td,
                "rel_kind": rk,
                "strength": ie["strength"],
                "score": ie["score"],
                "tier": ie["tier"],
                "count": 1,
                "pairs": [{"from_art_no": "Overview", "to_art_no": "Overview", "from_seq": 0, "to_seq": 0, "score": ie["score"], "strength": ie["strength"], "note": ie["note"]}],
            }

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

    # 按 (准则体系, 领域) + 单片 ~1.2MB 上限切分全文检索分片（彻底消除单体大文件，支持按体系/领域按需加载）
    out_ft_dir.mkdir(parents=True, exist_ok=True)
    old_monolith = out_data_dir / "fulltext.js"
    if old_monolith.exists():
        old_monolith.unlink()

    fw_dom_by_doc = {d["id"]: (d.get("framework", "CN"), d["domain"]) for d in documents}
    rows_by_bucket: dict[tuple[str, str], list[list]] = defaultdict(list)
    for r in fulltext_rows:
        rows_by_bucket[fw_dom_by_doc.get(r[0], ("CN", "general"))].append(r)

    ft_shards_meta: list[dict] = []
    written_ft_files: set[str] = set()
    bucket_order = [
        ("CN", "tax"), ("CN", "general"), ("CN", "audit"), ("CN", "accounting"),
        ("INTL", "accounting"), ("INTL", "audit"), ("INTL", "tax"), ("INTL", "general"),
        ("US", "accounting"), ("US", "audit"), ("US", "tax"), ("US", "general"),
    ]
    for fw, dom in bucket_order:
        dom_rows = rows_by_bucket.get((fw, dom), [])
        if not dom_rows:
            continue
        chunk: list[list] = []
        chunk_bytes = 0
        shard_idx = 0
        fw_prefix = "" if fw == "CN" else f"{fw.lower()}_"

        def flush_chunk(c_rows: list[list], idx: int) -> None:
            shard_id = f"{fw_prefix}{dom}_{idx}"
            fname = f"ft_{shard_id}.js"
            fpath = out_ft_dir / fname
            payload_str = (
                f'window.__finlexFtShardLoaded("{shard_id}",'
                + json.dumps(c_rows, ensure_ascii=False, separators=(",", ":"))
                + ");\n"
            )
            fpath.write_text(payload_str, encoding="utf-8")
            written_ft_files.add(fname)
            ft_shards_meta.append(
                {
                    "id": shard_id,
                    "framework": fw,
                    "domain": dom,
                    "file": f"ft/{fname}",
                    "rows": len(c_rows),
                    "kb": round(fpath.stat().st_size / 1024, 1),
                }
            )

        for r in dom_rows:
            r_bytes = len(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) + 1
            if chunk and chunk_bytes + r_bytes > FT_SHARD_MAX_BYTES:
                flush_chunk(chunk, shard_idx)
                shard_idx += 1
                chunk = []
                chunk_bytes = 0
            chunk.append(r)
            chunk_bytes += r_bytes
        if chunk:
            flush_chunk(chunk, shard_idx)

    for stale in out_ft_dir.glob("ft_*.js"):
        if stale.name not in written_ft_files:
            stale.unlink()

    index_payload = {
        "meta": {
            "built_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "document_count": len(documents),
            "article_count": sum(len(v) for v in articles_by_doc.values()),
            "raw_link_count": len(raw_links),
            "doc_link_count": len(doc_links),
            "connected_doc_count": sum(1 for d in documents if d["total_degree"] > 0),
            "ft_shards": ft_shards_meta,
        },
        "taxonomy": {
            "frameworks": FRAMEWORK_META,
            "domains": DOMAIN_META,
            "doc_types": DOC_TYPE_META,
            "statuses": STATUS_META,
            "topics": topics_list,
        },
        "documents": documents,
        "doc_links": doc_links,
    }

    # 写出首屏索引与按文档条文分片
    out_docs_dir.mkdir(parents=True, exist_ok=True)
    index_js_path = out_data_dir / "index.js"
    index_js_path.write_text(
        "window.FINLEX_INDEX = " + json.dumps(index_payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    # 构建单条法条级精准关联（直接嵌入各文档的 doc_<id>.js，保持首屏 index.js 体积零增加）
    art_links_raw: dict[int, list[dict]] = defaultdict(list)
    doc_art_counts = {did: len(al) for did, al in articles_by_doc.items()}
    for row in raw_links:
        fd = row["from_doc_id"]
        td = row["to_doc_id"]
        if fd not in doc_ids_set or td not in doc_ids_set or fd == td:
            continue
        f_aid = row["from_article_id"]
        t_aid = row["to_article_id"]
        f_seq = int(row["from_seq"] or 0)
        t_seq = int(row["to_seq"] or 0)
        score = int(row["score"] or 60)
        tier = row["tier"] or "L3"
        rel_kind = row["rel_kind"] or "cites"
        note, _ = clean_text(row["note"])

        # 多条法规的首条（seq=0）跳过纯文档级 seq=0 <-> seq=0 泛化兜底边（已在顶部全貌胶囊条呈现）
        is_generic_root = (f_seq == 0 and t_seq == 0)
        if not (is_generic_root and doc_art_counts.get(fd, 0) >= 5):
            art_links_raw[f_aid].append(
                {
                    "doc_id": td,
                    "tier": tier,
                    "score": score,
                    "rel_kind": rel_kind,
                    "target_seq": t_seq,
                    "target_art_no": (row["to_art_no"] or "").strip(),
                    "dir": "out",
                    "note": note,
                }
            )
        if not (is_generic_root and doc_art_counts.get(td, 0) >= 5):
            art_links_raw[t_aid].append(
                {
                    "doc_id": fd,
                    "tier": tier,
                    "score": score,
                    "rel_kind": rel_kind,
                    "target_seq": f_seq,
                    "target_art_no": (row["from_art_no"] or "").strip(),
                    "dir": "in",
                    "note": note,
                }
            )

    for did, art_list in articles_by_doc.items():
        for a in art_list:
            raw_al = art_links_raw.get(a["id"])
            if not raw_al:
                continue
            # 按 (doc_id, target_seq) 去重取最高分，按分值降序最多保留 12 条高价值条文关联
            best_al: dict[tuple[int, int], dict] = {}
            for item in raw_al:
                k = (item["doc_id"], item["target_seq"])
                if k not in best_al or item["score"] > best_al[k]["score"]:
                    best_al[k] = item
            sorted_al = sorted(best_al.values(), key=lambda x: (-x["score"], x["doc_id"], x["target_seq"]))[:12]
            if sorted_al:
                a["links"] = sorted_al

    written_doc_files: set[str] = set()
    for doc_id in doc_ids_set:
        doc_payload = {"id": doc_id, "articles": articles_by_doc.get(doc_id, [])}
        fname = f"doc_{doc_id}.js"
        doc_js_path = out_docs_dir / fname
        doc_js_path.write_text(
            f"window.__finlexDocLoaded({doc_id}," + json.dumps(doc_payload, ensure_ascii=False, separators=(",", ":")) + ");\n",
            encoding="utf-8",
        )
        written_doc_files.add(fname)

    # 自动清理已删除文档遗留的旧分片文件
    for stale_doc in out_docs_dir.glob("doc_*.js"):
        if stale_doc.name not in written_doc_files:
            stale_doc.unlink()

    if TEMPLATE_PATH.exists():
        out_html_path.write_text(TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    topic_counts = Counter(d["topic_label"] for d in documents)
    ft_total_kb = round(sum(s["kb"] for s in ft_shards_meta), 1)
    ft_max_kb = max((s["kb"] for s in ft_shards_meta), default=0.0)
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
        "ft_shards": len(ft_shards_meta),
        "ft_total_kb": ft_total_kb,
        "ft_max_shard_kb": ft_max_kb,
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
