#!/usr/bin/env python3
"""
FinLex 法条精准关联与五层全貌评分引擎（零第三方依赖，需 Python 3.9+）

设计目标：
用户检索任意法案或准则时，快速看清该法规的「完整全貌」：
- L1 核心落地配套（90–100 分）：同号应用指南、财政部实施问答、法律实施条例、审计问题解答、效力沿革
- L2 正式修补与权威解答（75–89 分）：企业会计准则解释第1–20号（精确到具体第X项）、监管适用指引、司法解释、上位授权法
- L3 条文级精准引用（60–74 分）：全库正文显式《法规名》第X条抽取（精确落到目标具体条号，过滤泛化首条套话噪音）
- L4 跨域实务衔接（45–59 分）：精选去重单向「会—税—审—商」衔接桥梁（杜绝双向重复边）
- L5 实务案例与官方解读（25–44 分）：按显式引用与业务关键词自动挂接实务案例与官方解读（后续新增案例重跑即自动关联）
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT.parent / "finlex" / "backend" / "data" / "finlex.db"

CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNITS = {"十": 10, "百": 100, "千": 1000}


def cn_to_int(s: str) -> int | None:
    s = s.strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    total = 0
    num = 0
    for ch in s:
        if ch in CN_DIGITS:
            num = CN_DIGITS[ch]
        elif ch in CN_UNITS:
            unit = CN_UNITS[ch]
            if num == 0:
                num = 1
            total += num * unit
            num = 0
        else:
            return None
    return total + num if (total + num) > 0 else None


def normalize_title(t: str) -> str:
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[（(][^（）()]*?(?:修订|修正|发布|试行|财会)[^（）()]*?[）)]", "", t)
    t = t.replace("—", "——").replace("————", "——")
    t = re.sub(r"第0+(\d+)号", r"第\1号", t)
    return t.strip()


def score_to_strength(score: int) -> str:
    if score >= 75:
        return "strong"
    if score >= 45:
        return "medium"
    return "weak"


def score_to_tier(score: int) -> str:
    if score >= 90:
        return "L1"
    if score >= 75:
        return "L2"
    if score >= 60:
        return "L3"
    if score >= 45:
        return "L4"
    return "L5"


# 同准则家族内条文级语义锚定：通用法条停用词（过滤高频套话，保留高区分度业务术语）
TERM_STOPWORDS = {
    "企业", "应当", "按照", "本准则", "规定", "相关", "下列", "有关", "会计", "处理", "进行",
    "确认", "计量", "披露", "附注", "财务", "报表", "项目", "金额", "发生", "或者", "以及",
    "可以", "不得", "包括", "是指", "情形", "条件", "资产", "负债", "损益", "当期", "期间",
    "以后", "之前", "以上", "以下", "其他", "其中", "同时", "满足", "符合", "适用", "除外",
    "根据", "依据", "通过", "方式", "方法", "原则", "标准", "要求", "信息", "说明", "情况",
    "影响", "变动", "变化", "调整", "计算", "确定", "判断", "评估", "估计", "分析", "考虑",
    "存在", "具有", "构成", "属于", "作为", "计入", "转入", "形成", "产生", "导致", "引起",
    "一项", "一定", "一般", "通常", "合理", "可靠", "主要", "重要", "重大", "具体", "相应",
    "分别", "各自", "全部", "部分", "相同", "不同", "上述", "前述", "该项", "本条", "前款",
}

# 财税审高区分度业务短语（命中时给予更高语义权重）
DOMAIN_ANCHOR_PHRASES = [
    "主要责任人", "代理人", "可变对价", "合同履约成本", "合同取得成本", "合同资产", "合同负债",
    "销售退回", "质量保证", "质保", "客户额外购买选择权", "授予知识产权许可", "售后回购",
    "售后租回", "使用权资产", "租赁负债", "租赁变更", "短期租赁", "低价值资产租赁", "转租赁",
    "可变租赁付款额", "融资租赁", "经营租赁", "租金减让",
    "合同变更", "履约义务", "单独售价", "交易价格", "重大融资成分", "非现金对价", "应付客户对价",
    "某一时段内", "某一时点", "履约进度", "控制权", "预收款", "现金折扣", "亏损合同", "储值卡", "购物卡",
    "权益法", "成本法", "共同控制", "重大影响", "初始投资成本", "商誉", "公允价值", "账面价值",
    "非同一控制", "同一控制", "反向购买", "补偿性资产", "分步实现", "合并对价",
    "预期信用损失", "信用减值", "三阶段", "金融负债", "权益工具", "永续债", "回售权", "减资",
    "套期保值", "公允价值套期", "现金流量套期", "金融资产转移", "终止确认", "继续涉入",
    "以权益结算", "以现金结算", "可行权条件", "等待期", "授予日", "限制性股票", "股票期权", "集团股份支付",
    "暂时性差异", "递延所得税资产", "递延所得税负债", "计税基础", "初始确认豁免", "单项交易",
    "可兑换性", "即期汇率", "记账本位币", "外币财务报表折算",
    "研究阶段", "开发阶段", "内部研发", "无形资产摊销", "使用寿命不确定",
    "预定可使用状态", "固定资产折旧", "弃置费用", "更新改造", "持有待售", "处置组", "终止经营",
    "与资产相关", "与收益相关", "政府补助", "总额法", "净额法", "财政贴息",
    "专门借款", "一般借款", "资本化期间", "暂停资本化", "停止资本化",
    "债务重组", "债权人", "债务人", "以资产清偿债务", "债转股", "修改其他条款",
    "非货币性资产交换", "商业实质", "换入资产", "换出资产",
    "PPP项目合同", "社会资本方", "无形资产模式", "金融资产模式", "混合模式",
    "设定受益计划", "设定提存计划", "辞退福利", "离职后福利", "短期薪酬",
    "关联方", "关键管理人员", "资金集中管理", "现金流量表", "经营活动", "投资活动", "筹资活动",
]


def extract_semantic_tokens(text: str) -> Counter[str]:
    """提取文本中的高辨识度中文业务术语与 3-4 字片段，用于同准则家族内条文锚定。"""
    if not text:
        return Counter()
    counts: Counter[str] = Counter()
    for ph in DOMAIN_ANCHOR_PHRASES:
        c = text.count(ph)
        if c > 0:
            counts[f"P:{ph}"] += c * 3
    # 提取连续中文片段中的 2-4 字高区分度词
    for seg in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        L = len(seg)
        if L <= 4:
            if seg not in TERM_STOPWORDS:
                counts[seg] += 1
        else:
            for n in (3, 4):
                for i in range(0, min(L - n + 1, 24)):
                    gram = seg[i : i + n]
                    if gram not in TERM_STOPWORDS:
                        counts[gram] += 1
    return counts


def build_standard_term_index(std_arts: list[dict]) -> dict | None:
    """为单部准则的非首条正文构建条文级 IDF 语义索引。"""
    cand_arts = [a for a in std_arts if a["seq"] > 0 and len(a["text_raw"] or "") >= 20]
    if len(cand_arts) < 3:
        return None
    doc_freq: Counter[str] = Counter()
    art_vecs: list[tuple[dict, Counter[str]]] = []
    for a in cand_arts:
        toks = extract_semantic_tokens(f"{a['heading'] or ''} {a['text_raw'] or ''}")
        art_vecs.append((a, toks))
        for t in toks:
            doc_freq[t] += 1
    N = len(cand_arts)
    idf = {t: math.log((N + 1.0) / (df + 0.5)) + 1.0 for t, df in doc_freq.items() if df <= max(3, int(N * 0.45))}
    return {"idf": idf, "art_vecs": art_vecs}


def match_child_to_standard_articles(
    child_heading: str,
    child_text: str,
    std_index: dict | None,
    std_art_num_map: dict[int, int],
    top_k: int = 2,
) -> list[tuple[int, str]]:
    """将同准则家族的子条文（指南分节/实施问答/官方案例）锚定到主准则具体条文，返回 [(to_art_id, reason), ...]。"""
    # 1) 优先检测显式同准则条号引用（如「本准则第三十四条」「该准则第16条」）
    explicit_hits: list[tuple[int, str]] = []
    seen_ids: set[int] = set()
    head_and_lead = f"{child_heading or ''} {(child_text or '')[:1600]}"
    for m in re.finditer(r"(?:本准则|该准则|新收入准则|收入准则|租赁准则|金融工具准则|股份支付准则|长投准则|企业会计准则第\s*0*\d+\s*号[^第]{0,16})第([一二三四五六七八九十百千0-9]+)条", head_and_lead):
        n = cn_to_int(m.group(1))
        if n and n > 1 and n in std_art_num_map:
            aid = std_art_num_map[n]
            if aid not in seen_ids:
                seen_ids.add(aid)
                explicit_hits.append((aid, f"显式指向第{n}条"))
                if len(explicit_hits) >= top_k:
                    return explicit_hits
    if explicit_hits:
        return explicit_hits

    if not std_index:
        return []

    # 2) 同准则家族内 IDF 语义重合打分（标题 3x 权重 + 正文前 1800 字）
    q_toks = extract_semantic_tokens(f"{child_heading or ''} {child_heading or ''} {child_heading or ''} {(child_text or '')[:1800]}")
    if not q_toks:
        return []
    idf = std_index["idf"]
    scored: list[tuple[float, list[str], dict]] = []
    for art, a_toks in std_index["art_vecs"]:
        score = 0.0
        shared_phrases: list[str] = []
        for t, q_cnt in q_toks.items():
            if t not in a_toks or t not in idf:
                continue
            w = idf[t] * math.log1p(min(q_cnt, 6)) * math.log1p(min(a_toks[t], 6))
            if t.startswith("P:"):
                w *= 2.8
                shared_phrases.append(t[2:])
            score += w
        if score > 0:
            scored.append((score, shared_phrases, art))

    if not scored:
        return []
    scored.sort(key=lambda x: -x[0])
    best_score = scored[0][0]
    # 严格置信门槛：需要达到较高重合分值（含专业术语命中更易过阈）
    min_threshold = 9.0 if scored[0][1] else 14.0
    if best_score < min_threshold:
        return []

    results: list[tuple[int, str]] = []
    for sc, phrases, art in scored[:top_k]:
        if sc < max(min_threshold, best_score * 0.62):
            break
        kw_tag = "、".join(phrases[:2]) if phrases else "条文主题匹配"
        results.append((art["id"], f"锚定{art['article_no']}（{kw_tag}）"))
    return results


# 财政部实施问答 -> 对应准则编号（0 表示基本准则，'small' 表示小企业会计准则，'ppp' 特殊处理）
MOF_QA_MAP: dict[str, list[int | str]] = {
    "存货准则": [1],
    "长期股权投资准则": [2],
    "固定资产准则": [4],
    "资产减值准则": [8],
    "股份支付准则": [11],
    "债务重组准则": [12],
    "收入准则": [14],
    "PPP会计处理": ["interp:14"],
    "政府补助准则": [16],
    "借款费用准则": [17],
    "外币折算准则": [19],
    "企业合并准则": [20],
    "租赁准则": [21],
    "金融工具准则": [22, 23, 24, 37],
    "新保险合同准则": [25],
    "会计政策、会计估计变更和差错更正准则": [28],
    "财务报表列报准则": [30],
    "现金流量表准则": [31],
    "合并财务报表准则": [33],
    "首次执行准则": [38],
    "其他相关": [0],
    "小企业会计准则": ["small"],
}

# 审计准则问题解答编号 -> 核心对应审计准则编号
AUDIT_QA_CSA_MAP: dict[int, list[int]] = {
    1: [1101, 1141],
    2: [1312],
    3: [1311],
    4: [1141, 1211, 1231],
    5: [1141, 1211, 1231],
    6: [1323],
    7: [1141, 1231],
    8: [1221, 1251],
    9: [1121, 5101, 5102],
    10: [1401],
    11: [1321],
    12: [1301, 1312],
    13: [1324],
    14: [1504],
    15: [1521],
    16: [1502],
    17: [1321],
    18: [1141, 1301],
    19: [1141, 1211],
}

# L4 精选跨域实务衔接（单向去重：仅在两文档无更高层级直接关联时生成）
CURATED_CROSS_DOMAIN: list[tuple[str, str, int, str]] = [
    ("cas:14", "tax:vat", 56, "业财税衔接：会计收入确认时点与增值税纳税义务发生时间差异"),
    ("cas:14", "tax:cit", 56, "业财税衔接：会计收入确认与企业所得税应税收入口径差异"),
    ("cas:14", "audit_qa:4", 58, "会审衔接：收入确认舞弊风险评估与审计应对"),
    ("cas:14", "reg:audit_2", 56, "会审衔接：收入审计中的职业怀疑与监管重点"),
    ("cas:1", "audit_qa:3", 56, "会审衔接：存货核算与存货监盘审计程序"),
    ("cas:1", "audit_csa:1311", 52, "会审衔接：存货计量与特定项目审计证据"),
    ("cas:4", "tax:cit", 54, "税会衔接：固定资产折旧年限、加速折旧与税前扣除差异"),
    ("cas:6", "tax:cit", 54, "税会衔接：无形资产摊销与研发费用税前加计扣除"),
    ("cas:6", "tax:rd", 56, "税会衔接：研发支出资本化/费用化与研发费用加计扣除政策"),
    ("cas:8", "audit_qa:17", 56, "会审衔接：资产/商誉减值测试与审计估值复核"),
    ("cas:9", "tax:iit", 54, "税会衔接：职工薪酬核算与个人所得税代扣代缴"),
    ("cas:9", "tax:cit", 54, "税会衔接：职工福利费、教育经费等薪酬税前扣除限额"),
    ("cas:11", "tax:iit", 54, "税会衔接：股份支付会计确认与股权激励个人所得税"),
    ("cas:11", "tax:cit", 52, "税会衔接：股份支付等待期费用与企业所得税税前扣除"),
    ("cas:12", "tax:cit", 52, "税会衔接：债务重组损益的会计确认与特殊性税务处理"),
    ("cas:16", "tax:cit", 54, "税会衔接：政府补助与企业所得税不征税收入认定"),
    ("cas:18", "tax:cit", 58, "税会核心衔接：暂时性差异、递延所得税与企业所得税汇算清缴"),
    ("cas:18", "tax:cit_reg", 55, "税会衔接：税前扣除标准差异对递延所得税的影响"),
    ("cas:20", "law:company", 54, "法财衔接：企业合并重组与公司法股权/合并程序"),
    ("cas:2", "law:company", 54, "法财衔接：长期股权投资出资、表决权与利润分配"),
    ("cas:33", "law:company", 52, "法财衔接：控制权认定与母子公司法人治理"),
    ("cas:21", "tax:vat", 52, "税会衔接：使用权资产/租赁负债与租赁业务增值税处理"),
    ("cas:21", "tax:cit", 52, "税会衔接：新租赁准则折旧利息拆分与租金税前扣除差异"),
    ("cas:22", "audit_qa:11", 54, "会审衔接：金融工具预期信用损失与会计估计审计"),
    ("cas:36", "tax:admin", 54, "税会衔接：关联方披露与税收征管法转让定价特别纳税调整"),
    ("cas:36", "audit_qa:6", 56, "会审衔接：关联方识别、披露与关联交易审计应对"),
    ("cas:36", "reg:risk_9", 54, "监管衔接：控股股东资金占用识别与关联交易审计"),
    ("cas:39", "audit_qa:11", 52, "会审衔接：公允价值估值层级与会计估计审计"),
    ("small_cas", "tax:small_cit", 55, "小微衔接：小企业会计核算与小型微利企业所得税优惠"),
    ("small_cas", "tax:small_vat", 54, "小微衔接：小企业核算与增值税小规模纳税人减免政策"),
    ("tax:vat", "tax:invoice", 56, "征管衔接：增值税计税凭证与发票开具/合规管理"),
    ("tax:vat", "tax:cit", 50, "税种衔接：增值税销售额与企业所得税应税收入比对"),
    ("audit_csa:1502", "reg:audit_1", 58, "监管衔接：非无保留意见准则与证监会审计类第1号指引"),
    ("audit_csa:1141", "law:criminal_12", 52, "法审衔接：财务舞弊审计应对与刑法背信/舞弊追责"),
]

# L5 财政部官方《企业会计准则应用案例》专题 -> 对应核心准则
MOF_CASE_MAP: dict[str, list[int | str]] = {
    "股份支付准则应用案例": [11],
    "收入准则应用案例": [14],
    "PPP会计处理应用案例": [14, "interp:14"],
    "所得税准则应用案例": [18],
    "外币折算准则应用案例": [19],
    "企业合并准则应用案例": [20],
    "租赁准则应用案例": [21],
    "金融工具准则应用案例": [22, 23, 24, 37],
}

# L5 案例关键词兜底规则（供未来新增案例自动归属）
CASE_KEYWORD_RULES: list[tuple[list[str], str, str]] = [
    (["虚开", "增值税专用发票", "增值税发票"], "tax:invoice", "实务案例参考：虚开增值税发票违法认定"),
    (["虚开", "增值税"], "tax:vat", "实务案例参考：增值税违规处理与稽查"),
    (["偷税", "逃税", "隐匿收入", "少缴税款"], "tax:admin", "实务案例参考：偷税/逃避缴纳税款处罚依据"),
    (["个人所得税", "主播", "网红", "个税"], "tax:iit", "实务案例参考：个人所得税申报与补税处罚"),
    (["企业所得税"], "tax:cit", "实务案例参考：企业所得税稽查与调整"),
    (["出口退税", "骗取出口退税"], "tax:vat", "实务案例参考：骗取出口退税违法查处"),
    (["出口退税", "骗取出口退税"], "tax:admin", "实务案例参考：出口退税征管与处罚"),
    (["固定资产", "折旧", "安装完毕", "预定可使用状态"], "cas:4", "实务案例参考：固定资产折旧起始时点判断"),
    (["固定资产", "折旧", "安装完毕", "预定可使用状态"], "cas_guide:4", "实务案例参考：固定资产应用指南实务落地"),
]


def ensure_columns(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(article_links)").fetchall()}
    if "score" not in cols:
        conn.execute("ALTER TABLE article_links ADD COLUMN score INTEGER DEFAULT 60")
    if "tier" not in cols:
        conn.execute("ALTER TABLE article_links ADD COLUMN tier VARCHAR(8) DEFAULT 'L3'")


def rebuild_links(db_path: Path) -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)
    cur = conn.cursor()

    docs = [dict(r) for r in cur.execute("SELECT * FROM documents ORDER BY id ASC")]
    doc_by_id = {d["id"]: d for d in docs}
    arts = [dict(r) for r in cur.execute("SELECT id, document_id, article_no, heading, text_raw, seq FROM articles ORDER BY document_id, seq, id")]

    first_art_by_doc: dict[int, int] = {}
    art_num_map: dict[int, dict[int, int]] = defaultdict(dict)
    arts_by_doc: dict[int, list[dict]] = defaultdict(list)

    for a in arts:
        did = a["document_id"]
        arts_by_doc[did].append(a)
        if did not in first_art_by_doc:
            first_art_by_doc[did] = a["id"]
        ano = (a["article_no"] or "").strip()
        m_num = re.match(r"^第([一二三四五六七八九十百千0-9]+)[条项节部分]", ano)
        if m_num:
            n = cn_to_int(m_num.group(1))
            if n is not None and n not in art_num_map[did]:
                art_num_map[did][n] = a["id"]

    # 构建关键文档别名与语义键映射
    key_to_doc: dict[str, int] = {}
    cas_std_by_num: dict[int, int] = {}
    cas_guide_by_num: dict[int, int] = {}
    csa_by_num: dict[int, int] = {}
    audit_qa_by_num: dict[int, int] = {}
    interp_by_num: dict[int, int] = {}
    alias_to_doc: dict[str, int] = {}

    for d in docs:
        did = d["id"]
        t = d["title"]
        nt = normalize_title(t)
        alias_to_doc[nt] = did
        if t.startswith("中华人民共和国"):
            alias_to_doc[normalize_title(t.replace("中华人民共和国", "", 1))] = did

        # 会计准则
        if d["domain"] == "accounting" and d["doc_type"] == "standard":
            if "基本准则" in t and "可持续" not in t:
                cas_std_by_num[0] = did
                key_to_doc["cas:0"] = did
                alias_to_doc["企业会计准则——基本准则"] = did
                alias_to_doc["基本准则"] = did
            elif "小企业会计准则" in t:
                key_to_doc["small_cas"] = did
                alias_to_doc["小企业会计准则"] = did
            else:
                m = re.search(r"企业会计准则第0*(\d+)号", t)
                if m:
                    num = int(m.group(1))
                    cas_std_by_num[num] = did
                    key_to_doc[f"cas:{num}"] = did
                    alias_to_doc[f"企业会计准则第{num}号"] = did

        # 应用指南
        if d["domain"] == "accounting" and "应用指南" in t and d["status"] == "in_force":
            if "基本准则" in t and "可持续" not in t:
                cas_guide_by_num[0] = did
                key_to_doc["cas_guide:0"] = did
            else:
                m = re.search(r"企业会计准则第0*(\d+)号——(.+?)应用指南", t)
                if m and "原保险合同" not in t:
                    num = int(m.group(1))
                    cas_guide_by_num[num] = did
                    key_to_doc[f"cas_guide:{num}"] = did

        # 准则解释
        m_int = re.match(r"^企业会计准则解释第(\d+)号$", t)
        if m_int:
            num = int(m_int.group(1))
            interp_by_num[num] = did
            key_to_doc[f"interp:{num}"] = did

        # 审计准则 & 问题解答
        m_csa = re.search(r"中国注册会计师(?:审计|其他鉴证业务|审阅|相关服务)准则第(\d+)号", t)
        if m_csa and "问题解答" not in t:
            num = int(m_csa.group(1))
            csa_by_num[num] = did
            key_to_doc[f"audit_csa:{num}"] = did
            alias_to_doc[f"中国注册会计师审计准则第{num}号"] = did
            alias_to_doc[f"审计准则第{num}号"] = did
        m_aqa = re.search(r"审计准则问题解答第(\d+)号", t)
        if m_aqa:
            num = int(m_aqa.group(1))
            audit_qa_by_num[num] = did
            key_to_doc[f"audit_qa:{num}"] = did

        # 税务/综合关键标识
        if t == "中华人民共和国增值税法":
            key_to_doc["tax:vat"] = did
            alias_to_doc["增值税暂行条例"] = did
            alias_to_doc["中华人民共和国增值税暂行条例"] = did
        elif t == "中华人民共和国增值税法实施条例":
            key_to_doc["tax:vat_reg"] = did
        elif t == "中华人民共和国企业所得税法":
            key_to_doc["tax:cit"] = did
        elif t == "中华人民共和国企业所得税法实施条例":
            key_to_doc["tax:cit_reg"] = did
        elif t == "中华人民共和国个人所得税法":
            key_to_doc["tax:iit"] = did
        elif t == "中华人民共和国个人所得税法实施条例":
            key_to_doc["tax:iit_reg"] = did
        elif t == "中华人民共和国税收征收管理法":
            key_to_doc["tax:admin"] = did
            alias_to_doc["税收征管法"] = did
        elif t == "中华人民共和国发票管理办法":
            key_to_doc["tax:invoice"] = did
        elif "研发费用税前加计扣除" in t:
            key_to_doc["tax:rd"] = did
        elif "小型微利企业所得税优惠政策征管问题" in t and d["doc_type"] == "normative":
            key_to_doc["tax:small_cit"] = did
        elif "增值税小规模纳税人减免增值税" in t:
            key_to_doc["tax:small_vat"] = did
        elif "会计法" in t:
            key_to_doc["law:accounting"] = did
        elif "公司法" in t:
            key_to_doc["law:company"] = did
        elif "证券法" in t:
            key_to_doc["law:securities"] = did
        elif "注册会计师法（2014" in t:
            key_to_doc["law:cpa_2014"] = did
        elif "注册会计师法（2026" in t:
            key_to_doc["law:cpa_2026"] = did
        elif "刑法修正案（十二）" in t:
            key_to_doc["law:criminal_12"] = did
        elif "会计监管风险提示第9号" in t:
            key_to_doc["reg:risk_9"] = did
        elif "审计类第1号" in t:
            key_to_doc["reg:audit_1"] = did
        elif "审计类第2号" in t:
            key_to_doc["reg:audit_2"] = did

    # 候选边容器：key=(from_art_id, to_art_id, rel_kind) -> dict
    candidates: list[dict] = []
    # 记录已存在的高优无向文档对（L1/L2/L3），供 L4 去重
    high_tier_pairs: set[tuple[int, int]] = set()
    # 记录已添加的无向单边对（防止 L1/L4 双向重复）
    undirected_seen: set[tuple[int, int, str]] = set()

    def add_link(
        from_doc: int,
        to_doc: int,
        rel_kind: str,
        score: int,
        note: str,
        from_art: int | None = None,
        to_art: int | None = None,
        link_type: str = "related",
        dedup_undirected: bool = False,
    ) -> None:
        if from_doc == to_doc:
            return
        fa = from_art or first_art_by_doc.get(from_doc)
        ta = to_art or first_art_by_doc.get(to_doc)
        if not fa or not ta:
            return
        pair = (min(from_doc, to_doc), max(from_doc, to_doc))
        if dedup_undirected:
            if (pair[0], pair[1], rel_kind) in undirected_seen:
                return
            undirected_seen.add((pair[0], pair[1], rel_kind))
        if score >= 60:
            high_tier_pairs.add(pair)
        candidates.append(
            {
                "from_doc": from_doc,
                "to_doc": to_doc,
                "from_art": fa,
                "to_art": ta,
                "link_type": link_type,
                "rel_kind": rel_kind,
                "score": score,
                "tier": score_to_tier(score),
                "strength": score_to_strength(score),
                "note": note[:240],
            }
        )

    # ==========================================================
    # L1: 核心落地配套（90–100 分）
    # ==========================================================
    # 1.1 效力沿革链（replaced_by_doc_id）
    for d in docs:
        rep_id = d.get("replaced_by_doc_id")
        if rep_id and rep_id in doc_by_id:
            add_link(d["id"], rep_id, "superseded_by", 98, f"效力沿革：已被《{doc_by_id[rep_id]['title']}》替代", link_type="supersedes", dedup_undirected=True)

    # 预构建全部核心会计准则的条文级语义索引（供同准则家族指南/问答/官方案例下沉）
    std_term_indices: dict[int, dict | None] = {}
    for sd_id in set(cas_std_by_num.values()):
        std_term_indices[sd_id] = build_standard_term_index(arts_by_doc.get(sd_id, []))
    if "small_cas" in key_to_doc:
        sc_id = key_to_doc["small_cas"]
        std_term_indices[sc_id] = build_standard_term_index(arts_by_doc.get(sc_id, []))

    # 1.2 应用指南 -> 同号企业会计准则（分节精准下沉至具体条文 + 文档保底）
    for d in docs:
        if d["domain"] == "accounting" and "应用指南" in d["title"] and d["id"] not in (89, 90):
            target_std_id = None
            base_lbl = "核心配套：《应用指南汇编2024》实务指南与例题"
            sc = 96 if d["status"] == "in_force" else 88
            if "原保险合同" in d["title"] and 25 in cas_std_by_num:
                target_std_id = cas_std_by_num[25]
                base_lbl = "核心配套：2024汇编原保险合同应用指南"
                sc = 93
            elif "基本准则" in d["title"] and "可持续" not in d["title"] and 0 in cas_std_by_num:
                target_std_id = cas_std_by_num[0]
                base_lbl = "核心配套：《应用指南汇编2024》基本准则详解"
            elif "可持续披露准则——基本准则" in d["title"]:
                for sd in docs:
                    if sd["doc_type"] == "standard" and "可持续披露准则——基本准则" in sd["title"]:
                        target_std_id = sd["id"]
                        base_lbl = "核心配套：可持续披露基本准则官方应用指南"
                        break
            else:
                m = re.search(r"企业会计准则第0*(\d+)号", d["title"])
                if m and int(m.group(1)) in cas_std_by_num:
                    target_std_id = cas_std_by_num[int(m.group(1))]
                    if d["status"] != "in_force":
                        base_lbl = "对应旧版应用指南（2006版）"

            if not target_std_id:
                continue
            # 始终保留 1 条文档级首条总配套，确保全貌层不漏连
            add_link(d["id"], target_std_id, "companion", sc, base_lbl, link_type="guidance", dedup_undirected=True)
            # 2024 现行指南分节语义下沉至具体条文
            if d["status"] == "in_force" and target_std_id in std_term_indices:
                for sec in arts_by_doc.get(d["id"], []):
                    if sec["seq"] == 0 and len(arts_by_doc.get(d["id"], [])) > 2:
                        continue
                    hits = match_child_to_standard_articles(
                        sec["heading"] or "",
                        sec["text_raw"] or "",
                        std_term_indices.get(target_std_id),
                        art_num_map[target_std_id],
                        top_k=2,
                    )
                    for to_aid, reason in hits:
                        add_link(
                            d["id"],
                            target_std_id,
                            "companion",
                            96,
                            f"指南详解（{sec['article_no'] or ''}{('·' + sec['heading'][:16]) if sec['heading'] else ''}）：{reason}",
                            from_art=sec["id"],
                            to_art=to_aid,
                            link_type="guidance",
                        )

    # 1.3 法律 <-> 实施条例（解析「XX法第X条所称」实现逐条精准 L1 下沉）
    for reg_key, law_key, law_short, desc in (
        ("tax:vat_reg", "tax:vat", "增值税法", "核心配套：增值税法国务院实施条例"),
        ("tax:cit_reg", "tax:cit", "企业所得税法", "核心配套：企业所得税法国务院实施条例"),
        ("tax:iit_reg", "tax:iit", "个人所得税法", "核心配套：个人所得税法国务院实施条例"),
    ):
        if reg_key in key_to_doc and law_key in key_to_doc:
            reg_id, law_id = key_to_doc[reg_key], key_to_doc[law_key]
            add_link(reg_id, law_id, "companion", 96, desc, link_type="guidance", dedup_undirected=True)
            law_cite_re = re.compile(rf"{re.escape(law_short)}第([一二三四五六七八九十百千0-9]+)条")
            for ra in arts_by_doc.get(reg_id, []):
                rtxt = ra["text_raw"] or ""
                seen_law_nums: set[int] = set()
                for lm in law_cite_re.finditer(rtxt):
                    lnum = cn_to_int(lm.group(1))
                    if lnum and lnum in art_num_map[law_id] and lnum not in seen_law_nums:
                        seen_law_nums.add(lnum)
                        add_link(
                            reg_id,
                            law_id,
                            "companion",
                            96,
                            f"实施条例细化：{ra['article_no'] or ''}解释{law_short}第{lnum}条",
                            from_art=ra["id"],
                            to_art=art_num_map[law_id][lnum],
                            link_type="guidance",
                        )

    # 1.4 财政部实施问答 -> 对应准则（单题精准下沉至具体条文 + 文档保底）
    for d in docs:
        if "实施问答" not in d["title"]:
            continue
        matched_any = False
        for kw, targets in MOF_QA_MAP.items():
            if kw in d["title"]:
                for tgt in targets:
                    tdid = None
                    if isinstance(tgt, int):
                        tdid = cas_std_by_num.get(tgt)
                    elif tgt == "small":
                        tdid = key_to_doc.get("small_cas")
                    elif tgt.startswith("interp:"):
                        tdid = key_to_doc.get(tgt)
                    if tdid:
                        add_link(d["id"], tdid, "companion", 94, "核心配套：财政部会计司官方实施问答", link_type="guidance", dedup_undirected=True)
                        if tdid in std_term_indices:
                            for qa in arts_by_doc.get(d["id"], []):
                                hits = match_child_to_standard_articles(
                                    qa["heading"] or "",
                                    qa["text_raw"] or "",
                                    std_term_indices.get(tdid),
                                    art_num_map[tdid],
                                    top_k=1,
                                )
                                for to_aid, reason in hits:
                                    add_link(
                                        d["id"],
                                        tdid,
                                        "companion",
                                        94,
                                        f"实施问答（{qa['article_no'] or ''}）：{reason}",
                                        from_art=qa["id"],
                                        to_art=to_aid,
                                        link_type="guidance",
                                    )
                        matched_any = True
                if matched_any:
                    break

    # 1.5 审计准则问题解答 -> 对应审计准则
    for qa_num, qa_doc_id in audit_qa_by_num.items():
        for csa_num in AUDIT_QA_CSA_MAP.get(qa_num, []):
            if csa_num in csa_by_num:
                add_link(qa_doc_id, csa_by_num[csa_num], "companion", 92, "核心配套：中注协审计准则官方问题解答", link_type="guidance", dedup_undirected=True)

    # ==========================================================
    # L2: 正式修补与权威解答（75–89 分）
    # ==========================================================
    # 2.1 企业会计准则解释第1–20号：逐项精准挂接所修订/解释的具体准则
    cas_cite_re = re.compile(r"《企业会计准则第\s*0*(\d+)\s*号[^《》]*》(?:第([一二三四五六七八九十百千0-9]+)条)?")
    for inum, idoc_id in interp_by_num.items():
        for a in arts_by_doc.get(idoc_id, []):
            txt = f"{a['heading'] or ''} {a['text_raw'] or ''}"
            seen_targets: set[int] = set()
            for m in cas_cite_re.finditer(txt):
                cnum = int(m.group(1))
                tdid = cas_std_by_num.get(cnum)
                if not tdid or tdid in seen_targets:
                    continue
                seen_targets.add(tdid)
                t_art_no = cn_to_int(m.group(2)) if m.group(2) else None
                to_art_id = art_num_map[tdid].get(t_art_no) if t_art_no else first_art_by_doc.get(tdid)
                exact_tag = f"（定位至第{t_art_no}条）" if (t_art_no and t_art_no in art_num_map[tdid]) else ""
                add_link(
                    idoc_id,
                    tdid,
                    "amends",
                    86,
                    f"正式修订/解释：{doc_by_id[idoc_id]['title']}{a['article_no'] or ''}{exact_tag}",
                    from_art=a["id"],
                    to_art=to_art_id,
                    link_type="amends",
                )

    # 2.2 监管指引、司法解释、上位授权法、税收专项政策公告
    l2_explicit_pairs: list[tuple[str, str, int, str]] = [
        ("cas:0", "law:accounting", 84, "上位授权依据：《会计法》授权制定企业会计准则体系"),
        ("small_cas", "law:accounting", 82, "上位授权依据：《会计法》小企业会计核算依据"),
        ("tax:invoice", "tax:admin", 84, "配套行政规章：依据《税收征收管理法》制定"),
        ("tax:small_vat", "tax:vat", 84, "专项优惠政策：增值税小规模纳税人减免口径"),
        ("tax:rd", "tax:cit", 84, "专项优惠政策：研发费用企业所得税加计扣除"),
        ("tax:small_cit", "tax:cit", 84, "专项优惠政策：小型微利企业所得税优惠征管"),
        ("reg:audit_1", "audit_csa:1502", 85, "监管适用指引：非标准审计意见合规边界"),
        ("reg:audit_2", "audit_csa:1141", 85, "监管适用指引：收入审计中的舞弊风险与职业怀疑"),
        ("reg:risk_9", "audit_csa:1323", 84, "监管风险提示：控股股东资金占用关联方审计"),
    ]
    for k1, k2, sc, note in l2_explicit_pairs:
        if k1 in key_to_doc and k2 in key_to_doc:
            add_link(key_to_doc[k1], key_to_doc[k2], "amends", sc, note, dedup_undirected=True)

    # 最高法规定 / 备案办法 / 小微税费政策 / 会计档案管理办法
    for d in docs:
        t = d["title"]
        if "会计档案管理办法" in t and "law:accounting" in key_to_doc:
            add_link(d["id"], key_to_doc["law:accounting"], "amends", 82, "配套部门规章：依据《会计法》制定", dedup_undirected=True)
        elif "审计业务活动中民事侵权赔偿" in t and "law:cpa_2014" in key_to_doc:
            add_link(d["id"], key_to_doc["law:cpa_2014"], "amends", 84, "司法解释：会计师事务所审计民事侵权赔偿规则", dedup_undirected=True)
        elif "证券市场虚假陈述侵权民事赔偿" in t and "law:securities" in key_to_doc:
            add_link(d["id"], key_to_doc["law:securities"], "amends", 84, "司法解释：证券虚假陈述民事赔偿规则", dedup_undirected=True)
        elif "从事证券服务业务备案管理办法" in t:
            if "law:securities" in key_to_doc:
                add_link(d["id"], key_to_doc["law:securities"], "amends", 82, "配套监管办法：证券服务机构备案管理", dedup_undirected=True)
            if "law:cpa_2026" in key_to_doc:
                add_link(d["id"], key_to_doc["law:cpa_2026"], "amends", 80, "配套监管办法：会计师事务所执业备案", dedup_undirected=True)
        elif "进一步支持小微企业和个体工商户发展有关税费政策" in t:
            for tk in ("tax:cit", "tax:vat", "tax:iit"):
                if tk in key_to_doc:
                    add_link(d["id"], key_to_doc[tk], "amends", 82, "专项优惠政策：小微企业与个体工商户税费减免", dedup_undirected=True)

    # ==========================================================
    # L3: 条文级精准引用（60–74 分，精确解析《法规名》第X条）
    # ==========================================================
    umbrella_docs = {
        key_to_doc[k]
        for k in ("cas:0", "law:accounting", "tax:admin", "law:company", "law:securities", "law:cpa_2014", "law:cpa_2026")
        if k in key_to_doc
    }
    full_cite_re = re.compile(r"《([^《》]{2,48})》(?:第([一二三四五六七八九十百千0-9]+)条)?")

    def resolve_alias(raw_name: str) -> int | None:
        norm = normalize_title(raw_name)
        if norm in alias_to_doc:
            return alias_to_doc[norm]
        # 匹配企业会计准则第X号
        m_cas = re.search(r"企业会计准则第0*(\d+)号", norm)
        if m_cas:
            return cas_std_by_num.get(int(m_cas.group(1)))
        # 匹配审计准则第XXXX号
        m_csa = re.search(r"审计准则第(\d+)号", norm)
        if m_csa:
            return csa_by_num.get(int(m_csa.group(1)))
        # 匹配准则解释第X号
        m_in = re.search(r"企业会计准则解释第(\d+)号", norm)
        if m_in:
            return interp_by_num.get(int(m_in.group(1)))
        return None

    # 收集已有 L1 companion 无向对，避免 L3 对同对文档再生成非精确条号冗余引用
    l1_companion_pairs = {
        (min(c["from_doc"], c["to_doc"]), max(c["from_doc"], c["to_doc"]))
        for c in candidates
        if c["tier"] == "L1"
    }

    pair_l3_count: Counter[tuple[int, int]] = Counter()
    seen_l3_exact: set[tuple[int, int]] = set()

    for d in docs:
        fdid = d["id"]
        if d["doc_type"] in ("case", "interpretation") or fdid in (89, 90):
            continue
        is_interp = fdid in interp_by_num.values()

        # 先收集该文档内所有显式引用，按「精确条号优先」排序
        raw_matches: list[tuple[int, int, int, int, int | None, str]] = []
        for a in arts_by_doc.get(fdid, []):
            txt = a["text_raw"] or ""
            for m in full_cite_re.finditer(txt):
                cited_name = m.group(1).strip()
                cited_art_str = m.group(2)
                tdid = resolve_alias(cited_name)
                if not tdid or tdid == fdid or tdid in (89, 90):
                    continue
                # 准则解释对 CAS 的引用已在 L2 处理，跳过重复 L3
                if is_interp and tdid in cas_std_by_num.values():
                    continue
                t_art_no = cn_to_int(cited_art_str) if cited_art_str else None
                has_exact = bool(t_art_no and t_art_no in art_num_map[tdid])
                if (min(fdid, tdid), max(fdid, tdid)) in l1_companion_pairs and not has_exact:
                    continue
                # 过滤泛化首条套话噪音（如所有 42 份会计准则第一条都写“根据《基本准则》，制定本准则”）
                if a["seq"] == 0 and tdid in umbrella_docs and not has_exact:
                    continue
                if tdid == key_to_doc.get("cas:0") and not has_exact:
                    continue
                to_art_id = art_num_map[tdid][t_art_no] if has_exact else first_art_by_doc.get(tdid)
                if not to_art_id:
                    continue
                raw_matches.append((1 if has_exact else 0, a["id"], tdid, to_art_id, t_art_no if has_exact else None, cited_name))

        # 精确条号优先
        raw_matches.sort(key=lambda x: (-x[0], x[2], x[1]))
        for has_exact, fa_id, tdid, ta_id, exact_no, cname in raw_matches:
            if (fa_id, ta_id) in seen_l3_exact:
                continue
            # 每对文档最多保留 6 条最具代表性的条文级引用，避免过度冗余
            if pair_l3_count[(fdid, tdid)] >= 6:
                continue
            # 若目标为高频泛化大法且无精确条号，每对文档仅保留 1 条
            if tdid in umbrella_docs and not has_exact and pair_l3_count[(fdid, tdid)] >= 1:
                continue
            seen_l3_exact.add((fa_id, ta_id))
            pair_l3_count[(fdid, tdid)] += 1
            sc = 72 if has_exact else 64
            exact_suffix = f"第{exact_no}条" if exact_no else ""
            add_link(
                fdid,
                tdid,
                "cites",
                sc,
                f"正文显式引用《{doc_by_id[tdid]['title']}》{exact_suffix}",
                from_art=fa_id,
                to_art=ta_id,
                link_type="cites",
            )

    # ==========================================================
    # L4: 跨域实务衔接（45–59 分，含高频核验条对条锚点）
    # ==========================================================
    CURATED_ARTICLE_CROSS: list[tuple[str, int, str, int, int, str]] = [
        ("cas:14", 4, "tax:vat", 28, 58, "税会条对条：收入控制权转移确认时点 ↔ 增值税纳税义务发生时间"),
        ("cas:14", 4, "tax:cit", 6, 56, "税会条对条：会计收入确认 ↔ 企业所得税收入总额口径"),
        ("cas:14", 34, "tax:vat", 7, 56, "税会条对条：主要责任人/代理人（总额/净额） ↔ 增值税价外销售额"),
        ("cas:4", 14, "tax:cit", 11, 56, "税会条对条：固定资产会计折旧 ↔ 企业所得税折旧税前扣除"),
        ("cas:4", 14, "tax:cit_reg", 60, 56, "税会条对条：会计折旧年限 ↔ 企业所得税法实施条例最低折旧年限"),
        ("cas:6", 7, "tax:cit", 30, 56, "税会条对条：内部研发研究/开发阶段划分 ↔ 研发费用加计扣除"),
        ("cas:6", 7, "tax:cit_reg", 95, 56, "税会条对条：无形资产研发支出 ↔ 研发费用加计扣除实施口径"),
        ("cas:16", 1, "tax:cit_reg", 26, 54, "税会条对条：政府补助会计处理 ↔ 企税不征税收入（财政拨款）"),
        ("cas:18", 7, "tax:cit", 5, 58, "税会条对条：资产负债账面价值与计税基础暂时性差异 ↔ 应纳税所得额"),
        ("cas:36", 1, "tax:admin", 36, 54, "税会条对条：关联方披露 ↔ 关联企业独立交易原则与特别纳税调整"),
    ]
    exact_cross_pairs: set[tuple[int, int]] = set()
    for k1, a1_no, k2, a2_no, sc, note in CURATED_ARTICLE_CROSS:
        d1, d2 = key_to_doc.get(k1), key_to_doc.get(k2)
        if not d1 or not d2 or d1 == d2:
            continue
        fa = art_num_map[d1].get(a1_no)
        ta = art_num_map[d2].get(a2_no)
        if fa and ta:
            add_link(d1, d2, "cross_domain", sc, note, from_art=fa, to_art=ta, link_type="thematic")
            exact_cross_pairs.add((min(d1, d2), max(d1, d2)))

    for k1, k2, sc, note in CURATED_CROSS_DOMAIN:
        d1 = key_to_doc.get(k1)
        d2 = key_to_doc.get(k2)
        if not d1 or not d2 or d1 == d2:
            continue
        pair = (min(d1, d2), max(d1, d2))
        if pair in high_tier_pairs or pair in exact_cross_pairs:
            continue
        add_link(d1, d2, "cross_domain", sc, note, link_type="thematic", dedup_undirected=True)

    # ==========================================================
    # L5: 实务案例与官方解读自动挂接（25–44 分，含单篇官方案例下沉至具体条文）
    # ==========================================================
    for d in docs:
        if d["doc_type"] not in ("case", "interpretation"):
            continue
        fdid = d["id"]
        rel_k = "applies_to" if d["doc_type"] == "case" else "explains"
        base_label = "实务案例涉及" if d["doc_type"] == "case" else "官方解读对应"

        matched_targets: set[int] = set()
        case_pair_cnt: Counter[int] = Counter()

        # 0) 财政部官方《企业会计准则应用案例》专题精准挂接主准则（单篇案例下沉至具体条文 + 文档保底）
        if d["doc_type"] == "case":
            for kw, targets in MOF_CASE_MAP.items():
                if kw in d["title"]:
                    for tgt in targets:
                        tdid = cas_std_by_num.get(tgt) if isinstance(tgt, int) else key_to_doc.get(tgt)
                        if tdid:
                            add_link(fdid, tdid, "applies_to", 44, "财政部会计司官方准则应用案例汇编", link_type="applies_to", dedup_undirected=True)
                            matched_targets.add(tdid)
                            case_pair_cnt[tdid] += 1
                            if tdid in std_term_indices:
                                for ca in arts_by_doc.get(fdid, []):
                                    hits = match_child_to_standard_articles(
                                        ca["heading"] or "",
                                        ca["text_raw"] or "",
                                        std_term_indices.get(tdid),
                                        art_num_map[tdid],
                                        top_k=1,
                                    )
                                    for to_aid, reason in hits:
                                        short_h = (ca["heading"] or "").split("——")[-1][:24]
                                        add_link(
                                            fdid,
                                            tdid,
                                            "applies_to",
                                            44,
                                            f"官方案例（{ca['article_no'] or ''}·{short_h}）：{reason}",
                                            from_art=ca["id"],
                                            to_art=to_aid,
                                            link_type="applies_to",
                                        )
                    break

        # 1) 显式引用匹配（按条精准挂接，每对文档最多保留 4 条代表性条文引用）
        for a in arts_by_doc.get(fdid, []):
            txt = f"{d['title']} {a['heading'] or ''} {a['text_raw'] or ''}"
            for m in full_cite_re.finditer(txt):
                tdid = resolve_alias(m.group(1).strip())
                if not tdid or tdid == fdid or tdid in (89, 90):
                    continue
                if case_pair_cnt[tdid] >= 4:
                    continue
                t_art_no = cn_to_int(m.group(2)) if m.group(2) else None
                has_exact = bool(t_art_no and t_art_no in art_num_map[tdid])
                if tdid == key_to_doc.get("cas:0") and not has_exact:
                    continue
                to_art_id = art_num_map[tdid][t_art_no] if has_exact else first_art_by_doc.get(tdid)
                sc = 40 if d["doc_type"] == "interpretation" else (42 if has_exact else 36)
                add_link(
                    fdid,
                    tdid,
                    rel_k,
                    sc,
                    f"{base_label}《{doc_by_id[tdid]['title']}》" + (f"第{t_art_no}条" if has_exact else ""),
                    from_art=a["id"],
                    to_art=to_art_id,
                    link_type=rel_k,
                )
                matched_targets.add(tdid)
                case_pair_cnt[tdid] += 1

        # 2) 案例关键词自动兜底（针对未写全称书名号的案例）
        if d["doc_type"] == "case":
            full_case_txt = d["title"] + " " + " ".join((a["text_raw"] or "")[:800] for a in arts_by_doc.get(fdid, []))
            for kws, tkey, note in CASE_KEYWORD_RULES:
                tdid = key_to_doc.get(tkey)
                if tdid and tdid not in matched_targets and any(kw in full_case_txt for kw in kws):
                    add_link(fdid, tdid, "applies_to", 30, note, link_type="applies_to")
                    matched_targets.add(tdid)

    # 写入数据库（先清空旧边再批量写入去重后的高质量边）
    # 同 (from_art, to_art, link_type) 取最高分
    best_by_key: dict[tuple[int, int, str], dict] = {}
    for c in candidates:
        k = (c["from_art"], c["to_art"], c["link_type"])
        prev = best_by_key.get(k)
        if prev is None or c["score"] > prev["score"]:
            best_by_key[k] = c

    final_edges = list(best_by_key.values())
    cur.execute("DELETE FROM article_links")
    cur.executemany(
        """
        INSERT INTO article_links (from_article_id, to_article_id, link_type, note, strength, rel_kind, score, tier)
        VALUES (:from_art, :to_art, :link_type, :note, :strength, :rel_kind, :score, :tier)
        """,
        final_edges,
    )
    conn.commit()

    # 统计新引擎效果
    connected = set()
    exact_target_cnt = 0
    art_seq = {a["id"]: a["seq"] for a in arts}
    for e in final_edges:
        connected.add(e["from_doc"])
        connected.add(e["to_doc"])
        if art_seq.get(e["to_art"], 0) > 0:
            exact_target_cnt += 1

    iso_by_dom = Counter(d["domain"] for d in docs if d["id"] not in connected)
    tier_counts = Counter(e["tier"] for e in final_edges)
    rel_counts = Counter(e["rel_kind"] for e in final_edges)
    conn.close()

    return {
        "total_docs": len(docs),
        "connected_docs": len(connected),
        "isolated_docs": len(docs) - len(connected),
        "isolated_by_domain": dict(iso_by_dom),
        "total_article_links": len(final_edges),
        "non_first_target_links": exact_target_cnt,
        "by_tier": dict(sorted(tier_counts.items())),
        "by_rel_kind": dict(rel_counts.most_common()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="重建 FinLex 法条精准关联与五层全貌评分引擎")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    stats = rebuild_links(args.db)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
