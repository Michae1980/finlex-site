#!/usr/bin/env python3
"""
从 MaoDocs（审计文库）https://docs.maoyanqing.com/accounting/ent/casc/
全量抓取财政部会计司官方发布的《企业会计准则应用案例》全部 8 大专题（40+ 篇官方案例，2018–2026）
并幂等写入 finlex.db（零第三方依赖，需 Python 3.9+）。

设计说明：
- 每个专题（股份支付、收入、PPP、所得税、外币折算、企业合并、租赁、金融工具）入库为 1 份
  doc_type='case'、domain='accounting'、issuer='财政部会计司' 的官方案例汇编文档；
- 专题内每篇具体官方应用案例作为 1 条 article（案例1、案例2...），完整保留案情、会计分析与账务处理；
- source_name='MaoDocs（审计文库）'，source_url 为专题目录页直达链接，供前端仅在完整文章底部展示信息来源；
- 幂等更新：按 title 查找已存在记录，重复运行不会产生重复文档。
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sqlite3
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT.parent / "finlex" / "backend" / "data" / "finlex.db"
BASE_URL = "https://docs.maoyanqing.com/accounting/ent/casc/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def fetch_html(url: str, timeout: int = 25) -> str:
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def format_table(match: re.Match) -> str:
    tbl_html = match.group(0)
    rows_out: list[str] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl_html, re.I | re.S):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.I | re.S)
        cleaned = []
        for c in cells:
            txt = re.sub(r"<br\s*/?>", " ", c, flags=re.I)
            txt = re.sub(r"<[^>]+>", "", txt)
            txt = re.sub(r"\s+", " ", html_lib.unescape(txt)).strip()
            cleaned.append(txt)
        if any(cleaned):
            rows_out.append(" | ".join(cleaned))
    return "\n" + "\n".join(rows_out) + "\n" if rows_out else "\n"


def html_to_clean_text(fragment: str) -> str:
    fragment = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<a[^>]+class=[\"'][^\"']*header-anchor[^\"']*[\"'][^>]*>.*?</a>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<table[^>]*>.*?</table>", format_table, fragment, flags=re.I | re.S)
    fragment = re.sub(r"</?(p|div|br|li|h[1-6]|blockquote|pre)[^>]*>", "\n", fragment, flags=re.I)
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html_lib.unescape(text)
    lines: list[str] = []
    for raw_ln in text.splitlines():
        ln = re.sub(r"[\t\r\u00a0]+", " ", raw_ln).strip()
        if not ln or ln in ("#", "上一页", "下一页", "目录"):
            continue
        if ln.startswith("说明：本资料来源于互联网") or ln.startswith("© 202"):
            continue
        lines.append(ln)
    return "\n".join(lines)


def parse_case_index(index_html: str) -> list[dict]:
    """
    从 /accounting/ent/casc/ 主页按 <h2> 分组解析出：
    [{ "topic_title": "收入准则应用案例", "topic_url": "...", "cases": [(case_title, case_url), ...] }, ...]
    """
    m_main = re.search(r"<main[^>]*>(.*?)</main>", index_html, re.I | re.S)
    body = m_main.group(1) if m_main else index_html
    mc = re.search(r"<footer\b", body, re.I)
    if mc:
        body = body[: mc.start()]

    h2_matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", body, re.I | re.S))
    topics: list[dict] = []
    for i, m in enumerate(h2_matches):
        topic_title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html_lib.unescape(m.group(1)))).strip().lstrip("#").strip()
        if not topic_title or "目录" in topic_title:
            continue
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        chunk = body[start:end]

        cases: list[tuple[str, str]] = []
        seen_urls: set[str] = set()
        for href, txt in re.findall(r"<a[^>]+href=[\"']([^\"']*?casc/[^\"']+\.html)[\"'][^>]*>(.*?)</a>", chunk, re.I | re.S):
            url = urllib.parse.urljoin(BASE_URL, href.strip())
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html_lib.unescape(txt))).strip()
            if url not in seen_urls and label:
                seen_urls.add(url)
                cases.append((label, url))

        if not cases:
            continue
        # 推导专题目录页 URL（取首个案例的父目录）
        first_url = cases[0][1]
        topic_url = first_url.rsplit("/", 1)[0] + "/"
        topics.append({"topic_title": topic_title, "topic_url": topic_url, "cases": cases})
    return topics


def parse_case_page(page_html: str) -> str:
    m_main = re.search(r"<main[^>]*>(.*?)</main>", page_html, re.I | re.S)
    main_html = m_main.group(1) if m_main else page_html
    m_h1 = re.search(r"<h1[^>]*>.*?</h1>", main_html, re.I | re.S)
    if m_h1:
        main_html = main_html[m_h1.end() :]
    for cut_pat in (
        r"<footer\b",
        r"<div[^>]+class=[\"'][^\"']*(?:page-nav|vp-page-nav|vp-page-meta)[^\"']*[\"']",
    ):
        mc = re.search(cut_pat, main_html, re.I)
        if mc:
            main_html = main_html[: mc.start()]
    txt = html_to_clean_text(main_html)
    # 剔除开头的“约XXXX字 大约X分钟”阅读时长提示
    lines = txt.splitlines()
    while lines and (re.match(r"^约\s*\d+\s*字", lines[0]) or re.match(r"^大约\s*\d+\s*分钟", lines[0]) or lines[0].startswith("最近更新")):
        lines.pop(0)
    return "\n".join(lines).strip()


def infer_latest_year(case_titles: list[str]) -> str:
    years: list[int] = []
    for t in case_titles:
        for ym in re.findall(r"[（(](20[12]\d)[）)]", t):
            years.append(int(ym))
    if not years:
        return "2024-01-01"
    return f"{max(years)}-01-01"


def upsert_case_topic(
    conn: sqlite3.Connection,
    topic_title: str,
    topic_url: str,
    entries: list[dict],
) -> tuple[int, str, int]:
    cur = conn.cursor()
    title = topic_title if topic_title.startswith("企业会计准则") or "PPP" in topic_title else f"企业会计准则应用案例——{topic_title}"
    latest_date = infer_latest_year([e["title"] for e in entries])
    total_chars = sum(len(e["body"]) for e in entries)
    summary = f"财政部会计司官方发布的{topic_title}汇编（共收录 {len(entries)} 篇官方案例，约 {total_chars:,} 字），涵盖典型业务场景、准则分析与会计处理参考。"

    row = cur.execute("SELECT id FROM documents WHERE title=?", (title,)).fetchone()
    if row:
        doc_id = row[0]
        action = "updated"
        cur.execute(
            """
            UPDATE documents
            SET doc_type='case', domain='accounting', doc_no='财政部会计司应用案例',
                issuer='财政部会计司', pub_date=?, effective_date=?, status='in_force',
                source_name='MaoDocs（审计文库）', source_url=?, summary=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (latest_date, latest_date, topic_url, summary, doc_id),
        )
        cur.execute("DELETE FROM articles WHERE document_id=?", (doc_id,))
    else:
        action = "inserted"
        cur.execute(
            """
            INSERT INTO documents (
                doc_type, domain, title, doc_no, issuer, pub_date, effective_date,
                status, source_name, source_url, summary
            ) VALUES ('case', 'accounting', ?, '财政部会计司应用案例', '财政部会计司', ?, ?, 'in_force', 'MaoDocs（审计文库）', ?, ?)
            """,
            (title, latest_date, latest_date, topic_url, summary),
        )
        doc_id = cur.lastrowid

    for idx, item in enumerate(entries):
        art_no = f"案例{idx + 1}"
        heading = item["title"][:120]
        body = item["body"]
        cur.execute(
            "INSERT INTO articles (document_id, article_no, heading, text_raw, seq) VALUES (?, ?, ?, ?, ?)",
            (doc_id, art_no, heading, body, idx),
        )

    return doc_id, action, len(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description="全量同步财政部《企业会计准则应用案例》（MaoDocs镜像）至 finlex.db")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    idx_html = fetch_html(BASE_URL)
    topics = parse_case_index(idx_html)

    conn = sqlite3.connect(str(args.db))
    inserted = 0
    updated = 0
    total_cases = 0
    total_chars = 0
    failed = 0
    details = []

    for tp in topics:
        entries: list[dict] = []
        for c_title, c_url in tp["cases"]:
            try:
                p_html = fetch_html(c_url)
                body = parse_case_page(p_html)
                if len(body) >= 40:
                    entries.append({"title": c_title, "url": c_url, "body": body})
                else:
                    failed += 1
                time.sleep(0.05)
            except Exception:
                failed += 1

        if entries:
            doc_id, action, cnt = upsert_case_topic(conn, tp["topic_title"], tp["topic_url"], entries)
            conn.commit()
            chars = sum(len(e["body"]) for e in entries)
            total_cases += cnt
            total_chars += chars
            if action == "inserted":
                inserted += 1
            else:
                updated += 1
            details.append({"topic": tp["topic_title"], "doc_id": doc_id, "action": action, "cases": cnt, "chars": chars})

    conn.close()
    print(
        json.dumps(
            {
                "topics_found": len(topics),
                "inserted": inserted,
                "updated": updated,
                "total_cases": total_cases,
                "total_chars": total_chars,
                "failed": failed,
                "details": details,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
