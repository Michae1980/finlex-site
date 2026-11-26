#!/usr/bin/env python3
"""
IFRS Accounting Standards 公开合规版采集脚本（零第三方依赖，需 Python 3.9+）

功能：
1. 免登录从 IFRS Foundation 官网 sitemap.xml 自动发现并抓取全部 IFRS 会计准则与解释公告公开页面
   （Conceptual Framework、Preface、IFRS 1–20、IAS 1–41、IFRIC、SIC、Practice Statements、IFRS for SMEs）；
2. 提取每份准则的官方定位与适用范围（About）、完整修订沿革（Standard history）与相关项目/实施支持，
   并自动解析生效日期、替代关系与现行效力状态；
3. 补充收录 IFRS Foundation 官方免登录公开的 IFRIC Agenda Decisions 议程决议汇编（至 Vol. 15）
   及国际四大会计师事务所（KPMG / EY / Deloitte / PwC）公开实务指引索引（仅保留公开摘要与权威外链，
   不搬运付费或受限版权全文）；
4. 幂等输出至 intl_data/ifrs_accounting.json，供 scripts/build_prototype.py 在构建期合并导出。
"""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import html as html_lib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "intl_data" / "ifrs_accounting.json"
SITEMAP_URL = "https://www.ifrs.org/sitemap.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

SKIP_SLUGS = {
    "Glossary",
    "bound-volume-viewer",
    "management-commentary-practice-statement",  # duplicate of management-commentary-practice-statement-1
}

# 明确已知的替代关系（code -> (status, replaced_by_code, note)）
SUPERSEDED_MAP: dict[str, tuple[str, str, str]] = {
    "IAS 1": ("will_replace", "IFRS 18", "Effective until superseded by IFRS 18 for annual reporting periods beginning on or after 1 January 2027."),
    "IAS 11": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
    "IAS 17": ("outdated", "IFRS 16", "Superseded by IFRS 16 Leases (effective 1 January 2019)."),
    "IAS 18": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
    "IFRS 4": ("outdated", "IFRS 17", "Superseded by IFRS 17 Insurance Contracts (effective 1 January 2023)."),
    "IFRS 14": ("will_replace", "IFRS 20", "Interim Standard to be superseded by IFRS 20 Regulatory Assets and Regulatory Liabilities (issued May 2026)."),
    "IFRIC 4": ("outdated", "IFRS 16", "Superseded by IFRS 16 Leases (effective 1 January 2019)."),
    "IFRIC 9": ("outdated", "IFRS 9", "Superseded by IFRS 9 Financial Instruments (effective 1 January 2018)."),
    "IFRIC 13": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
    "IFRIC 15": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
    "IFRIC 18": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
    "SIC-15": ("outdated", "IFRS 16", "Superseded by IFRS 16 Leases (effective 1 January 2019)."),
    "SIC-27": ("outdated", "IFRS 16", "Superseded by IFRS 16 Leases (effective 1 January 2019)."),
    "SIC-31": ("outdated", "IFRS 15", "Superseded by IFRS 15 Revenue from Contracts with Customers (effective 1 January 2018)."),
}

# 尚未生效的新准则（2026-11-25 基准）
UPCOMING_MAP: dict[str, tuple[str, str, str]] = {
    "IFRS 18": ("upcoming", "2027-01-01", "Issued April 2024; effective for annual reporting periods beginning on or after 1 January 2027 (early application permitted). Replaces IAS 1."),
    "IFRS 19": ("upcoming", "2027-01-01", "Issued May 2024 (amended August 2025); effective for annual reporting periods beginning on or after 1 January 2027 (early application permitted)."),
    "IFRS 20": ("upcoming", "2029-01-01", "Issued May 2026; supersedes IFRS 14 Regulatory Deferral Accounts. Check official IASB implementation timeline for early application."),
}

# 中国企业会计准则（CAS）与 IFRS 核心趋同对照（用于跨体系关联边）
CAS_IFRS_MAP: dict[str, list[tuple[str, str]]] = {
    "Conceptual Framework": [("企业会计准则——基本准则", "国际与国内概念框架对照")],
    "IAS 1": [("企业会计准则第30号——财务报表列报", "财务报表列报趋同对照")],
    "IFRS 18": [("企业会计准则第30号——财务报表列报", "新一代损益表列报与披露对照")],
    "IAS 2": [("企业会计准则第1号——存货", "存货准则趋同对照")],
    "IAS 7": [("企业会计准则第31号——现金流量表", "现金流量表趋同对照")],
    "IAS 8": [("企业会计准则第28号——会计政策、会计估计变更和差错更正", "会计政策与估计变更趋同对照")],
    "IAS 10": [("企业会计准则第29号——资产负债表日后事项", "日后事项趋同对照")],
    "IAS 12": [("企业会计准则第18号——所得税", "所得税准则趋同对照")],
    "IAS 16": [("企业会计准则第4号——固定资产", "固定资产准则趋同对照")],
    "IAS 19": [("企业会计准则第9号——职工薪酬", "职工薪酬准则趋同对照")],
    "IAS 20": [("企业会计准则第16号——政府补助", "政府补助准则趋同对照")],
    "IAS 21": [("企业会计准则第19号——外币折算", "外币折算准则趋同对照")],
    "IAS 23": [("企业会计准则第17号——借款费用", "借款费用准则趋同对照")],
    "IAS 24": [("企业会计准则第36号——关联方披露", "关联方披露趋同对照")],
    "IAS 26": [("企业会计准则第10号——企业年金基金", "退休福利计划/企业年金基金对照")],
    "IAS 27": [("企业会计准则第2号——长期股权投资", "单独财务报表与长投对照")],
    "IAS 28": [("企业会计准则第2号——长期股权投资", "联营与合营企业权益法对照")],
    "IAS 32": [("企业会计准则第37号——金融工具列报", "金融工具列报趋同对照")],
    "IAS 33": [("企业会计准则第34号——每股收益", "每股收益趋同对照")],
    "IAS 34": [("企业会计准则第32号——中期财务报告", "中期财务报告趋同对照")],
    "IAS 36": [("企业会计准则第8号——资产减值", "资产减值趋同对照")],
    "IAS 37": [("企业会计准则第13号——或有事项", "预计负债与或有事项趋同对照")],
    "IAS 38": [("企业会计准则第6号——无形资产", "无形资产准则趋同对照")],
    "IAS 40": [("企业会计准则第3号——投资性房地产", "投资性房地产趋同对照")],
    "IAS 41": [("企业会计准则第5号——生物资产", "生物资产准则趋同对照")],
    "IFRS 1": [("企业会计准则第38号——首次执行企业会计准则", "首次执行准则对照")],
    "IFRS 2": [("企业会计准则第11号——股份支付", "股份支付准则趋同对照")],
    "IFRS 3": [("企业会计准则第20号——企业合并", "企业合并准则趋同对照")],
    "IFRS 5": [("企业会计准则第42号——持有待售的非流动资产、处置组和终止经营", "持有待售与终止经营趋同对照")],
    "IFRS 6": [("企业会计准则第27号——石油天然气开采", "矿产/油气勘探开发对照")],
    "IFRS 7": [("企业会计准则第37号——金融工具列报", "金融工具披露趋同对照")],
    "IFRS 8": [("企业会计准则第35号——分部报告", "分部报告趋同对照")],
    "IFRS 9": [
        ("企业会计准则第22号——金融工具确认和计量", "金融工具确认与计量趋同对照"),
        ("企业会计准则第23号——金融资产转移", "金融资产终止确认趋同对照"),
        ("企业会计准则第24号——套期会计", "套期会计趋同对照"),
    ],
    "IFRS 10": [("企业会计准则第33号——合并财务报表", "合并财务报表趋同对照")],
    "IFRS 11": [("企业会计准则第40号——合营安排", "合营安排趋同对照")],
    "IFRS 12": [("企业会计准则第41号——在其他主体中权益的披露", "在其他主体权益披露趋同对照")],
    "IFRS 13": [("企业会计准则第39号——公允价值计量", "公允价值计量趋同对照")],
    "IFRS 15": [("企业会计准则第14号——收入", "收入准则趋同对照")],
    "IFRS 16": [("企业会计准则第21号——租赁", "租赁准则趋同对照")],
    "IFRS 17": [("企业会计准则第25号——保险合同", "保险合同准则趋同对照")],
    "IFRS for SMEs": [("小企业会计准则", "中小企业会计框架对照")],
}

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


class SectionParser(HTMLParser):
    """提取 IFRS 单准则页面主体区域内的标题与段落文本。"""

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[tuple[str, str]] = []  # (tag, text)
        self._capture_tag: str | None = None
        self._buf: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in ("script", "style", "noscript", "svg"):
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if t in ("h1", "h2", "h3", "h4", "p", "li"):
            if self._capture_tag:
                self._flush()
            self._capture_tag = t
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("script", "style", "noscript", "svg") and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if t == self._capture_tag:
            self._flush()

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and self._capture_tag:
            self._buf.append(data)

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", html_lib.unescape("".join(self._buf))).strip()
        if text:
            self.blocks.append((self._capture_tag or "p", text))
        self._capture_tag = None
        self._buf = []


def fetch_text(url: str, retries: int = 2) -> str:
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(0.8 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def slug_to_code_and_type(slug: str, h1_title: str) -> tuple[str, str, str]:
    """返回 (code, doc_type, series_badge)。"""
    s = slug.lower()
    if s == "conceptual-framework":
        return "Conceptual Framework", "standard", "Conceptual Framework"
    if s == "preface-to-ifrs-standards":
        return "Preface", "standard", "IFRS Preface"
    if s == "ifrs-for-smes":
        return "IFRS for SMEs", "standard", "IFRS for SMEs"
    if "practice-statement" in s:
        if "materiality" in s:
            return "Practice Statement 2", "guidance", "Practice Statement 2"
        return "Practice Statement 1", "guidance", "Practice Statement 1"

    m = re.match(r"^(ifrs|ias|ifric|sic)-(\d+)", s)
    if m:
        prefix = m.group(1).upper()
        num = m.group(2)
        if prefix == "SIC":
            code = f"SIC-{num}"
            return code, "guidance", f"SIC-{num}"
        if prefix == "IFRIC":
            code = f"IFRIC {num}"
            return code, "guidance", f"IFRIC {num}"
        code = f"{prefix} {num}"
        return code, "standard", code

    return h1_title[:32], "standard", "IFRS"


def extract_dates(text: str) -> tuple[str, str]:
    """从 About / History 文本中尽力提取 (pub_date, effective_date)。"""
    eff_date = ""
    m_eff = re.search(
        r"effective(?:\s+for\s+annual\s+(?:reporting\s+)?periods\s+beginning)?\s+on\s+or\s+after\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
        text,
        re.I,
    )
    if m_eff:
        day = int(m_eff.group(1))
        mon = MONTH_MAP.get(m_eff.group(2).lower(), "01")
        yr = m_eff.group(3)
        eff_date = f"{yr}-{mon}-{day:02d}"

    # 最近一次修订/发布月份
    pub_date = ""
    matches = re.findall(
        r"In\s+([A-Za-z]+)\s+(\d{4})[,\s]+(?:the\s+IASB|the\s+International\s+Accounting\s+Standards\s+Board|the\s+Committee)\s+(?:issued|amended|adopted|revised)",
        text,
        re.I,
    )
    if matches:
        mon_name, yr = matches[-1]
        mon = MONTH_MAP.get(mon_name.lower(), "01")
        pub_date = f"{yr}-{mon}-01"
    elif eff_date:
        pub_date = eff_date

    return pub_date, eff_date


def parse_ifrs_page(url: str) -> dict | None:
    slug = url.rstrip("/").split("/")[-1]
    if slug in SKIP_SLUGS:
        return None
    raw_html = fetch_text(url)

    start_idx = raw_html.find("standards-page-heading")
    if start_idx == -1:
        start_idx = raw_html.find("<h1")
    end_idx = raw_html.find("cookieconsentbanner")
    if end_idx == -1 or end_idx <= start_idx:
        end_idx = len(raw_html)
    body_html = raw_html[max(0, start_idx) : end_idx]

    parser = SectionParser()
    parser.feed(body_html)

    h1_title = ""
    sections: dict[str, list[str]] = {
        "About": [],
        "Standard history": [],
        "Related information": [],
    }
    cur_sec = "About"
    noise_exact = {
        "Follow", "Close", "Show Sections", "About", "Standard", "News",
        "You need to Sign in to use this feature",
        "Standard history", "Related active projects", "Related completed projects",
        "Related IFRS Standards", "Related IFRIC Interpretations",
        "Unconsolidated amendments", "Implementation support",
    }

    for tag, txt in parser.blocks:
        if tag == "h1" and not h1_title:
            h1_title = txt
            continue
        if txt.startswith("Follow - ") or txt == "You need to Sign in to use this feature":
            continue
        if txt == "About":
            cur_sec = "About"
            continue
        if txt == "Standard history":
            cur_sec = "Standard history"
            continue
        if txt in (
            "Related active projects",
            "Related completed projects",
            "Related IFRS Standards",
            "Related IFRIC Interpretations",
            "Unconsolidated amendments",
            "Implementation support",
        ):
            cur_sec = "Related information"
            sections[cur_sec].append(f"[{txt}]")
            continue
        if txt in noise_exact:
            continue
        if len(txt) < 12 and cur_sec == "About":
            continue
        sections[cur_sec].append(txt)

    if not h1_title:
        return None

    code, doc_type, series_badge = slug_to_code_and_type(slug, h1_title)
    display_title = h1_title
    if display_title.startswith(code):
        rem = display_title[len(code) :].lstrip(" :—-")
        if rem:
            display_title = rem

    about_paras = sections["About"]
    history_paras = sections["Standard history"]
    related_items = sections["Related information"]

    all_text = "\n".join(about_paras + history_paras)
    pub_date, eff_date = extract_dates(all_text)

    status = "in_force"
    version_level = ""
    version_note = ""
    replaced_by_code = ""

    if code in SUPERSEDED_MAP:
        status, replaced_by_code, version_note = SUPERSEDED_MAP[code]
        version_level = "will_replace" if status == "will_replace" else "conflict"
    elif code in UPCOMING_MAP:
        status, up_eff, version_note = UPCOMING_MAP[code]
        version_level = "upcoming"
        if not eff_date:
            eff_date = up_eff
    elif "superseded" in " ".join(about_paras[:2]).lower() or "withdrawn" in " ".join(about_paras[:2]).lower():
        status = "outdated"
        version_level = "conflict"
        version_note = "Superseded or withdrawn Standard (retained for historical reference)."

    summary = about_paras[0][:240] if about_paras else f"Official IFRS Foundation overview and amendment history for {h1_title}."

    articles: list[dict] = []
    seq = 0
    if about_paras:
        articles.append(
            {
                "no": "Overview",
                "heading": "Official Overview & Scope (IFRS Foundation)",
                "text": "\n\n".join(about_paras),
                "seq": seq,
            }
        )
        seq += 1

    if history_paras:
        # 每 3 段或单段拆分为可读条文，便于检索定位与折叠阅读
        chunk_size = 3
        for idx in range(0, len(history_paras), chunk_size):
            part = history_paras[idx : idx + chunk_size]
            part_no = f"History {idx // chunk_size + 1}" if len(history_paras) > chunk_size else "History"
            articles.append(
                {
                    "no": part_no,
                    "heading": "Standard History & Amendments",
                    "text": "\n\n".join(part),
                    "seq": seq,
                }
            )
            seq += 1

    if related_items:
        articles.append(
            {
                "no": "Support",
                "heading": "Related Projects & Implementation Support",
                "text": "\n".join(related_items[:30]),
                "seq": seq,
            }
        )
        seq += 1

    # 官方原文入口与公开合规说明
    ref_lines = [
        f"Official IFRS Foundation Page (English): {url}",
        "Access Note: Free access to the unaccompanied text of IFRS Accounting Standards on ifrs.org requires a free registered IFRS.org account; Basis for Conclusions and Illustrative Examples require an IFRS Digital Subscription.",
        "Public Companion Overview: KPMG Insights into IFRS — An Overview (Sept 2026): https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/ifrg/2026/isg-2026-insights-an-overview.pdf",
    ]
    if code == "IFRS 18":
        ref_lines.append("EY Applying IFRS — A Closer Look at IFRS 18 (Updated April 2026): https://www.ey.com/en_gl/technical/ifrs-technical-resources/applying-ifrs-a-closer-look-at-ifrs-18-updated-april-2026")
    elif code in ("IFRS 2", "IFRS 15", "IFRS 16", "IAS 33", "IFRS 13"):
        ref_lines.append("KPMG IFRS Accounting Toolkit (Standard Handbooks): https://kpmg.com/xx/en/what-we-do/services/audit/corporate-reporting-institute/ifrs/toolkit.html")

    articles.append(
        {
            "no": "References",
            "heading": "Official Text Link & Public Practical Guidance",
            "text": "\n".join(ref_lines),
            "seq": seq,
        }
    )

    # 自动提取正文中提及的其他 IFRS/IAS/IFRIC/SIC 编号用于构建国际准则内部关联网
    cited_codes: set[str] = set()
    for m in re.finditer(r"\b(IFRS|IAS|IFRIC)\s+(\d{1,2})\b", all_text):
        c = f"{m.group(1)} {m.group(2)}"
        if c != code:
            cited_codes.add(c)
    for m in re.finditer(r"\bSIC-(\d{1,2})\b", all_text):
        c = f"SIC-{m.group(1)}"
        if c != code:
            cited_codes.add(c)

    return {
        "code": code,
        "slug": slug,
        "framework": "INTL",
        "domain": "accounting",
        "doc_type": doc_type,
        "title": h1_title,
        "display_title": display_title,
        "series_badge": series_badge,
        "doc_no": code,
        "issuer": "IASB / IFRS Foundation" if not code.startswith(("IFRIC", "SIC")) else "IFRS Interpretations Committee",
        "pub_date": pub_date or "2026-01-01",
        "effective_date": eff_date or pub_date or "2026-01-01",
        "status": status,
        "version_level": version_level,
        "version_note": version_note,
        "replaced_by_code": replaced_by_code,
        "source_name": "IFRS Foundation",
        "source_url": url,
        "source_kind": "official",
        "summary": summary,
        "articles": articles,
        "cited_codes": sorted(cited_codes),
        "cas_links": CAS_IFRS_MAP.get(code, []),
    }


def build_curated_entries() -> list[dict]:
    """补充 2026 年最新发布的 IFRS 20、官方免登录 IFRIC 议程决议汇编及国际四大公开实务指南索引。"""
    return [
        {
            "code": "IFRS 20",
            "slug": "ifrs-20-regulatory-assets-and-regulatory-liabilities",
            "framework": "INTL",
            "domain": "accounting",
            "doc_type": "standard",
            "title": "IFRS 20 Regulatory Assets and Regulatory Liabilities",
            "display_title": "Regulatory Assets and Regulatory Liabilities",
            "series_badge": "IFRS 20",
            "doc_no": "IFRS 20",
            "issuer": "IASB / IFRS Foundation",
            "pub_date": "2026-05-27",
            "effective_date": "2029-01-01",
            "status": "upcoming",
            "version_level": "upcoming",
            "version_note": "Issued May 2026; supersedes IFRS 14 Regulatory Deferral Accounts.",
            "replaced_by_code": "",
            "source_name": "IFRS Foundation",
            "source_url": "https://www.ifrs.org/news-and-events/news/2026/05/iasb-issues-ifrs-20/",
            "source_kind": "official",
            "summary": "Issued by the IASB in May 2026, IFRS 20 establishes accounting requirements for regulatory assets, regulatory liabilities, regulatory income and regulatory expense, superseding IFRS 14.",
            "articles": [
                {
                    "no": "Overview",
                    "heading": "Official Overview & Objective (IASB, May 2026)",
                    "text": (
                        "In May 2026, the International Accounting Standards Board (IASB) issued IFRS 20 Regulatory Assets and Regulatory Liabilities. "
                        "IFRS 20 supersedes IFRS 14 Regulatory Deferral Accounts and fills a gap in IFRS Accounting Standards for entities subject to rate regulation.\n\n"
                        "Objective: Provide investors with transparent, comparable information about the effects of regulatory income, regulatory expense, regulatory assets and regulatory liabilities on an entity's financial performance and financial position."
                    ),
                    "seq": 0,
                },
                {
                    "no": "Official PDFs",
                    "heading": "Open Official IFRS Foundation Documents",
                    "text": (
                        "Official Press Release (May 27, 2026): https://www.ifrs.org/news-and-events/news/2026/05/iasb-issues-ifrs-20/\n"
                        "Project Summary (Open PDF): https://www.ifrs.org/content/dam/ifrs/project/rate-regulated-activities/standard/iasb-ifrs20-projectsummary.pdf\n"
                        "Feedback Statement (Open PDF): https://www.ifrs.org/content/dam/ifrs/project/rate-regulated-activities/standard/iasb-ifrs20-fbs.pdf\n"
                        "At a Glance One-Pager (Open PDF): https://www.ifrs.org/content/dam/ifrs/project/rate-regulated-activities/standard/iasb-ifrs20-one-page.pdf"
                    ),
                    "seq": 1,
                },
                {
                    "no": "Big Four Guide",
                    "heading": "Public Practical Guidance (EY)",
                    "text": (
                        "EY — Applying IFRS: A Closer Look at IFRS 20 (September 2026, Open PDF):\n"
                        "Page: https://www.ey.com/en_gl/technical/ifrs-technical-resources/applying-ifrs-a-closer-look-at-ifrs-20\n"
                        "PDF: https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/technical/ifrs-technical-resources/documents/ey-gl-applying-ifrs-20-september-2026.pdf"
                    ),
                    "seq": 2,
                },
            ],
            "cited_codes": ["IFRS 14", "IFRS 18"],
            "cas_links": [],
        },
        {
            "code": "IFRIC Agenda Decisions",
            "slug": "ifric-compilation-of-agenda-decisions",
            "framework": "INTL",
            "domain": "accounting",
            "doc_type": "guidance",
            "title": "IFRS Interpretations Committee — Compilation of Agenda Decisions (Volumes 1–15)",
            "display_title": "Compilation of Agenda Decisions (Vol. 1–15, through Oct 2026)",
            "series_badge": "Agenda Decisions",
            "doc_no": "IFRIC AD Vol. 1–15",
            "issuer": "IFRS Interpretations Committee",
            "pub_date": "2026-10-31",
            "effective_date": "2026-10-31",
            "status": "in_force",
            "version_level": "",
            "version_note": "",
            "replaced_by_code": "",
            "source_name": "IFRS Foundation",
            "source_url": "https://www.ifrs.org/news-and-events/updates/ifric/",
            "source_kind": "official",
            "summary": "Official open-access compilations of IFRIC Agenda Decisions explaining how existing IFRS Accounting Standards apply to practical questions, sorted by Standard through Volume 15 (May–Oct 2026).",
            "articles": [
                {
                    "no": "Role",
                    "heading": "Authority & Role of IFRIC Agenda Decisions",
                    "text": (
                        "The IFRS Interpretations Committee works with the IASB to support consistent application of IFRS Accounting Standards. "
                        "When an application question is submitted and the Committee concludes that existing principles and requirements in IFRS Accounting Standards provide an adequate basis for an entity to determine the required accounting, it publishes an Agenda Decision with explanatory material.\n\n"
                        "Agenda Decisions are subject to due process (normally 60-day comment period as Tentative Agenda Decisions) and are finalised only if fewer than four IASB members object. Entities are expected to have sufficient time to implement accounting changes resulting from Agenda Decisions."
                    ),
                    "seq": 0,
                },
                {
                    "no": "Latest Volumes",
                    "heading": "Direct Official Open PDFs (No Login Required)",
                    "text": (
                        "Volume 15 (May 2026 – October 2026): https://www.ifrs.org/content/dam/ifrs/supporting-implementation/agenda-decisions/agenda-decision-compilations/compilation-agenda-decisions-vol-15-may2026-oct2026.pdf\n"
                        "Volume 14 Announcement (November 2025 – April 2026): https://www.ifrs.org/news-and-events/news/2026/05/compilation-of-agenda-decisions-volume-14-published/\n"
                        "Volume 13 (May 2025 – October 2025): https://www.ifrs.org/content/dam/ifrs/supporting-implementation/agenda-decisions/agenda-decision-compilations/compilation-agenda-decisions-vol-13-may2025-oct2025.pdf\n"
                        "IFRIC Update Archive: https://www.ifrs.org/news-and-events/updates/ifric/"
                    ),
                    "seq": 1,
                },
            ],
            "cited_codes": ["IFRS 18", "IFRS 15", "IFRS 16", "IFRS 9", "IAS 12", "IAS 37"],
            "cas_links": [],
        },
        {
            "code": "Big4 Guide: KPMG",
            "slug": "kpmg-insights-into-ifrs-overview-2026",
            "framework": "INTL",
            "domain": "accounting",
            "doc_type": "interpretation",
            "title": "KPMG — Insights into IFRS: An Overview (2026 Edition) & IFRS Accounting Toolkit",
            "display_title": "KPMG Insights into IFRS: An Overview (2026) & Toolkit",
            "series_badge": "Big4 Guide · KPMG",
            "doc_no": "KPMG IFRS 2026",
            "issuer": "KPMG IFRG Limited",
            "pub_date": "2026-09-01",
            "effective_date": "2026-12-31",
            "status": "in_force",
            "version_level": "",
            "version_note": "",
            "replaced_by_code": "",
            "source_name": "KPMG",
            "source_url": "https://kpmg.com/xx/en/what-we-do/services/audit/corporate-reporting-institute/ifrs/toolkit.html",
            "source_kind": "third_party",
            "summary": "Public companion guide by KPMG (September 2026 edition) providing a topic-by-topic overview of key requirements across IFRS Accounting Standards for 31 December 2026 year-ends, plus free standard handbooks.",
            "articles": [
                {
                    "no": "Overview",
                    "heading": "Scope & Key Topics Covered (2026 Edition)",
                    "text": (
                        "KPMG's Insights into IFRS: An Overview (September 2026 edition) is designed for companies with a year-end of 31 December 2026. "
                        "It summarises key recognition, measurement, presentation and disclosure requirements across the Conceptual Framework, IAS 1 / forthcoming IFRS 18 & IFRS 19, consolidation (IFRS 10/11/12/IAS 27/28), fair value measurement (IFRS 13), financial instruments (IFRS 9/IAS 32/IFRS 7), revenue (IFRS 15), leases (IFRS 16), and impairment (IAS 36)."
                    ),
                    "seq": 0,
                },
                {
                    "no": "Public Links",
                    "heading": "Verified Public Resources & Handbooks",
                    "text": (
                        "Insights into IFRS — An Overview (Sept 2026 Open PDF): https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/ifrg/2026/isg-2026-insights-an-overview.pdf\n"
                        "KPMG IFRS Accounting Toolkit (Handbooks for IFRS 2, IFRS 15, IFRS 16, IAS 33, Fair Value, IFRS 18, IFRS vs US GAAP & 2026 Illustrative Disclosures): https://kpmg.com/xx/en/what-we-do/services/audit/corporate-reporting-institute/ifrs/toolkit.html\n"
                        "KPMG Global IFRS Hub: https://kpmg.com/xx/en/what-we-do/services/audit/corporate-reporting-institute/ifrs.html"
                    ),
                    "seq": 1,
                },
            ],
            "cited_codes": ["Conceptual Framework", "IFRS 18", "IFRS 19", "IFRS 9", "IFRS 13", "IFRS 15", "IFRS 16", "IFRS 10"],
            "cas_links": [],
        },
        {
            "code": "Big4 Guide: EY",
            "slug": "ey-applying-ifrs-technical-resources",
            "framework": "INTL",
            "domain": "accounting",
            "doc_type": "interpretation",
            "title": "EY — Applying IFRS Technical Resources (IFRS 18 & IFRS 20 Deep-Dive Guides)",
            "display_title": "EY Applying IFRS: IFRS 18 (Apr 2026) & IFRS 20 (Sep 2026)",
            "series_badge": "Big4 Guide · EY",
            "doc_no": "EY Applying IFRS 2026",
            "issuer": "EY Global IFRS",
            "pub_date": "2026-09-24",
            "effective_date": "2026-09-24",
            "status": "in_force",
            "version_level": "",
            "version_note": "",
            "replaced_by_code": "",
            "source_name": "EY",
            "source_url": "https://www.ey.com/en_gl/technical/ifrs-technical-resources/applying-ifrs-a-closer-look-at-ifrs-18-updated-april-2026",
            "source_kind": "third_party",
            "summary": "Public English technical guides by EY Global covering the latest major IFRS Accounting Standards, including IFRS 18 Presentation and Disclosure (updated April 2026) and IFRS 20 Regulatory Assets and Regulatory Liabilities (September 2026).",
            "articles": [
                {
                    "no": "IFRS 18 Guide",
                    "heading": "Applying IFRS: A Closer Look at IFRS 18 (Updated April 2026)",
                    "text": (
                        "Covers the new profit or loss categories and subtotals (operating profit; profit before financing and income taxes), management-defined performance measures (MPMs), aggregation/disaggregation principles, and practical illustrations and FAQs.\n"
                        "Official Page: https://www.ey.com/en_gl/technical/ifrs-technical-resources/applying-ifrs-a-closer-look-at-ifrs-18-updated-april-2026\n"
                        "Direct PDF: https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/technical/ifrs-technical-resources/documents/ey-gl-ifrs-apply-ifrs-18-updated-v2-04-2026.pdf"
                    ),
                    "seq": 0,
                },
                {
                    "no": "IFRS 20 Guide",
                    "heading": "Applying IFRS: A Closer Look at IFRS 20 (September 2026)",
                    "text": (
                        "Detailed technical walk-through of IFRS 20 Regulatory Assets and Regulatory Liabilities, covering scope, key concepts, recognition, measurement and transition from IFRS 14.\n"
                        "Official Page: https://www.ey.com/en_gl/technical/ifrs-technical-resources/applying-ifrs-a-closer-look-at-ifrs-20\n"
                        "Direct PDF: https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/technical/ifrs-technical-resources/documents/ey-gl-applying-ifrs-20-september-2026.pdf"
                    ),
                    "seq": 1,
                },
            ],
            "cited_codes": ["IFRS 18", "IFRS 20", "IAS 1", "IFRS 14"],
            "cas_links": [],
        },
        {
            "code": "Big4 Guide: Deloitte & PwC",
            "slug": "deloitte-iasplus-pwc-viewpoint-public-guides",
            "framework": "INTL",
            "domain": "accounting",
            "doc_type": "interpretation",
            "title": "Deloitte IAS Plus & PwC Viewpoint — Public IFRS Newsletters and Practical Guides",
            "display_title": "Deloitte IAS Plus (IFRS in Focus) & PwC Viewpoint Free Guides",
            "series_badge": "Big4 Guide · Deloitte / PwC",
            "doc_no": "Big4 Public Hub",
            "issuer": "Deloitte / PwC",
            "pub_date": "2026-09-01",
            "effective_date": "2026-09-01",
            "status": "in_force",
            "version_level": "",
            "version_note": "",
            "replaced_by_code": "",
            "source_name": "Deloitte & PwC",
            "source_url": "https://www.iasplus.com/en-ca/publications/ifrs-in-focus",
            "source_kind": "third_party",
            "summary": "Public English reference hubs from Deloitte IAS Plus (IFRS in Focus newsletters, model financial statements and IASB meeting summaries) and PwC Viewpoint free tier (In briefs, In depths and illustrative accounts).",
            "articles": [
                {
                    "no": "Deloitte IAS Plus",
                    "heading": "Deloitte IAS Plus — IFRS in Focus & Resource Library",
                    "text": (
                        "Deloitte IAS Plus provides free public newsletters (IFRS in Focus) covering new IFRS Accounting Standards, Conceptual Framework revisions, annual closing-out reminders, IASB/IFRIC meeting summaries, and jurisdiction adoption profiles.\n"
                        "IFRS in Focus Hub: https://www.iasplus.com/en-ca/publications/ifrs-in-focus\n"
                        "IASB Resources Library: https://www.iasplus.com/en/resources/ifrsf/history/resource47"
                    ),
                    "seq": 0,
                },
                {
                    "no": "PwC Viewpoint",
                    "heading": "PwC Viewpoint — Free Access Tier",
                    "text": (
                        "PwC Viewpoint allows free browsing without a paid subscription for news items, 'In briefs', 'In depths' practical guidance on current IFRS reporting issues, illustrative IFRS financial statements, and IFRS Talks podcasts.\n"
                        "PwC Viewpoint Overview: https://www.pwc.com/gx/en/services/audit-assurance/viewpoint.html"
                    ),
                    "seq": 1,
                },
            ],
            "cited_codes": ["Conceptual Framework", "IFRS 18", "IFRS 15", "IFRS 16", "IFRS 9"],
            "cas_links": [],
        },
    ]


def main() -> int:
    print("Fetching IFRS Foundation sitemap...", file=sys.stderr)
    sitemap_xml = fetch_text(SITEMAP_URL)
    urls = sorted(set(re.findall(r"<loc>([^<]+list-of-standards/[^<]+)</loc>", sitemap_xml)))
    urls.append("https://www.ifrs.org/issued-standards/ifrs-for-smes/")
    print(f"Discovered {len(urls)} candidate IFRS.org pages.", file=sys.stderr)

    docs: list[dict] = []
    errors: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        fut_map = {pool.submit(parse_ifrs_page, u): u for u in urls}
        for fut in concurrent.futures.as_completed(fut_map):
            u = fut_map[fut]
            try:
                item = fut.result()
                if item:
                    docs.append(item)
            except Exception as exc:
                errors.append(f"{u}: {exc}")

    # 合并精选补充条目（IFRS 20、IFRIC Agenda Decisions、四大公开实务指引）
    existing_codes = {d["code"] for d in docs}
    for extra in build_curated_entries():
        if extra["code"] not in existing_codes:
            docs.append(extra)

    # 按国际准则体系自然序排序：Conceptual Framework -> Preface -> IFRS 1..20 -> IAS 1..41 -> IFRIC -> SIC -> Practice Statements -> IFRS for SMEs -> Agenda Decisions -> Big4 Guides
    def sort_key(d: dict) -> tuple[int, int, str]:
        c = d["code"]
        if c == "Conceptual Framework":
            return (0, 0, c)
        if c == "Preface":
            return (0, 1, c)
        m = re.match(r"^IFRS (\d+)$", c)
        if m:
            return (1, int(m.group(1)), c)
        m = re.match(r"^IAS (\d+)$", c)
        if m:
            return (2, int(m.group(1)), c)
        m = re.match(r"^IFRIC (\d+)$", c)
        if m:
            return (3, int(m.group(1)), c)
        m = re.match(r"^SIC-(\d+)$", c)
        if m:
            return (4, int(m.group(1)), c)
        if c.startswith("Practice Statement"):
            return (5, 0, c)
        if c == "IFRS for SMEs":
            return (6, 0, c)
        if c == "IFRIC Agenda Decisions":
            return (7, 0, c)
        return (8, 0, c)

    docs.sort(key=sort_key)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "framework": "INTL",
        "domain": "accounting",
        "collected_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source_policy": "Public-compliant open metadata, official IFRS.org About/History, open IFRIC Agenda Decisions & Big Four public practical guidance references (English).",
        "document_count": len(docs),
        "documents": docs,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "output": str(OUT_PATH.relative_to(PROJECT_ROOT)),
        "documents": len(docs),
        "articles": sum(len(d["articles"]) for d in docs),
        "errors": len(errors),
        "error_samples": errors[:5],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
