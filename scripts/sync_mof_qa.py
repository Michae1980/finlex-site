#!/usr/bin/env python3
"""
从财政部会计司官网（kjs.mof.gov.cn/zt/kjzzss/sswd/）抓取官方免费公开的
「企业会计准则实施问答」并幂等写入 finlex.db（零第三方依赖，需 Python 3.9+）。

说明：
- 每个专题（如「收入准则实施问答」「租赁准则实施问答」「金融工具准则实施问答」等）入库为 1 份 guidance 文档；
- 专题内每条官方问答入库为 1 条 article（问1、问2...），保留完整提问与财政部官方解答正文；
- 自动提取每条问答页面发布日期，文档发布/生效日取该专题最新问答发布日期；
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
INDEX_URL = "https://kjs.mof.gov.cn/zt/kjzzss/sswd/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def fetch_html(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        raw = resp.read()
    for enc in ("utf-8", "gb18030", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"</?(p|div|br|li|tr|h[1-6])[^>]*>", "\n", fragment, flags=re.I)
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html_lib.unescape(text)
    lines = [re.sub(r"[\t\r \u3000]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def parse_categories(index_html: str) -> list[tuple[str, str]]:
    """从实施问答总页提取 (专题名称, 专题列表页URL)。"""
    cats: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    # 匹配形如 <h2>...<a href="./srzzsswd/">...</a> 或 标题 + 更多>> 链接
    pattern = re.compile(
        r"([^<>]{2,36}实施问答)\s*(?:</span>|</div>|</h\d>|</a>)?\s*<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>\s*更多",
        re.I | re.S,
    )
    for m in pattern.finditer(index_html):
        name = re.sub(r"\s+", "", html_lib.unescape(m.group(1)))
        href = urllib.parse.urljoin(INDEX_URL, m.group(2).strip())
        if href not in seen_urls:
            seen_urls.add(href)
            cats.append((name, href))
    if cats:
        return cats

    # 兜底：匹配所有 href 指向 sswd 下子目录的链接
    for m in re.finditer(r"<a[^>]+href=[\"'](\./[a-z0-9_]+/?)[\"'][^>]*>(.*?)</a>", index_html, re.I | re.S):
        href = urllib.parse.urljoin(INDEX_URL, m.group(1))
        label = strip_tags(m.group(2)).strip()
        if href not in seen_urls and label and "更多" not in label:
            seen_urls.add(href)
            cats.append((label, href))
    return cats


def parse_qa_links(cat_url: str, cat_html: str) -> list[tuple[str, str, str]]:
    """从专题列表页提取 (标题, 详情页URL, 日期YYYY-MM-DD)。支持翻页（index_1.htm 等）。"""
    items: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    def extract_page(page_url: str, page_html: str) -> None:
        # 匹配列表项 <a href="./202111/t20211102_3763218.htm" title="...">...</a>
        for m in re.finditer(
            r"<a[^>]+href=[\"']([^\"']*t(\d{4})(\d{2})(\d{2})_\d+\.htm[l]?)[\"'][^>]*>(.*?)</a>",
            page_html,
            re.I | re.S,
        ):
            href = urllib.parse.urljoin(page_url, m.group(1).strip())
            if href in seen:
                continue
            dt_str = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
            # 优先读 title 属性
            full_tag = m.group(0)
            mt = re.search(r"title=[\"']([^\"']+)[\"']", full_tag, re.I)
            title = html_lib.unescape(mt.group(1)).strip() if mt else strip_tags(m.group(5)).strip()
            if not title or len(title) < 4:
                continue
            seen.add(href)
            items.append((title, href, dt_str))

    extract_page(cat_url, cat_html)
    # 检查是否有翻页 index_1.htm / index_2.htm
    page_cnt_m = re.search(r"createPageHTML\(\s*(\d+)", cat_html)
    if page_cnt_m:
        total_pages = min(int(page_cnt_m.group(1)), 5)
        for p in range(1, total_pages):
            p_url = urllib.parse.urljoin(cat_url, f"index_{p}.htm")
            try:
                p_html = fetch_html(p_url)
                extract_page(p_url, p_html)
            except Exception:
                break
    return items


def parse_qa_body(detail_html: str) -> str:
    """提取财政部详情页正文。"""
    for pat in (
        r"<div[^>]+class=[\"'][^\"']*TRS_Editor[^\"']*[\"'][^>]*>(.*?)</div>\s*</div>",
        r"<div[^>]+class=[\"'][^\"']*my_doccontent[^\"']*[\"'][^>]*>(.*?)</div>",
        r"<div[^>]+id=[\"']Zoom[\"'][^>]*>(.*?)</div>",
        r"<div[^>]+class=[\"'][^\"']*box_content[^\"']*[\"'][^>]*>(.*?)</div>",
    ):
        m = re.search(pat, detail_html, re.I | re.S)
        if m:
            txt = strip_tags(m.group(1))
            if len(txt) >= 30:
                return txt
    # 兜底：取「问：」所在段落之后到页脚之前
    full = strip_tags(detail_html)
    idx = full.find("问：")
    if idx >= 0:
        end = full.find("附件下载", idx)
        if end < 0:
            end = full.find("网站地图", idx)
        return full[idx:end].strip() if end > idx else full[idx:].strip()
    return ""


def upsert_qa_doc(
    conn: sqlite3.Connection,
    cat_name: str,
    cat_url: str,
    qa_entries: list[dict],
) -> tuple[int, int]:
    cur = conn.cursor()
    title = cat_name if cat_name.startswith("企业会计准则") or "小企业" in cat_name or "PPP" in cat_name or "数据资源" in cat_name else f"企业会计准则实施问答——{cat_name.replace('实施问答', '')}"
    # 避免重复前缀
    title = title.replace("企业会计准则实施问答——新保险合同准则(财会[2020]20号)", "新保险合同准则（财会〔2020〕20号）实施问答")
    dates = [x["date"] for x in qa_entries if x.get("date")]
    latest_date = max(dates) if dates else "2026-01-01"
    summary = f"财政部会计司官方发布的{cat_name}汇编（共收录 {len(qa_entries)} 题，最新更新至 {latest_date}），用于补充现行企业会计准则实务操作口径。"

    row = cur.execute("SELECT id FROM documents WHERE title=?", (title,)).fetchone()
    if row:
        doc_id = row[0]
        cur.execute(
            """
            UPDATE documents
            SET pub_date=?, effective_date=?, status='in_force', source_name='财政部会计司',
                source_url=?, summary=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (latest_date, latest_date, cat_url, summary, doc_id),
        )
        cur.execute("DELETE FROM articles WHERE document_id=?", (doc_id,))
    else:
        cur.execute(
            """
            INSERT INTO documents (
                doc_type, domain, title, doc_no, issuer, pub_date, effective_date,
                status, source_name, source_url, summary
            ) VALUES ('guidance', 'accounting', ?, '财政部会计司实施问答', '财政部会计司', ?, ?, 'in_force', '财政部会计司', ?, ?)
            """,
            (title, latest_date, latest_date, cat_url, summary),
        )
        doc_id = cur.lastrowid

    for idx, qa in enumerate(qa_entries):
        art_no = f"问{idx + 1}"
        heading = qa["title"][:120]
        body = qa["body"]
        if qa.get("date"):
            body = f"【发布日期：{qa['date']}】\n{body}"
        cur.execute(
            """
            INSERT INTO articles (document_id, article_no, heading, text_raw, seq)
            VALUES (?, ?, ?, ?, ?)
            """,
            (doc_id, art_no, heading, body, idx),
        )
    return doc_id, len(qa_entries)


def main() -> int:
    parser = argparse.ArgumentParser(description="同步财政部会计司官方实施问答至 finlex.db")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--limit-cats", type=int, default=0, help="仅抓取前 N 个专题（0 为全部）")
    args = parser.parse_args()

    index_html = fetch_html(INDEX_URL)
    cats = parse_categories(index_html)
    if args.limit_cats > 0:
        cats = cats[: args.limit_cats]

    conn = sqlite3.connect(str(args.db))
    synced_docs = 0
    synced_qas = 0
    failed_urls = 0
    report = []

    for cat_name, cat_url in cats:
        try:
            cat_html = fetch_html(cat_url)
        except Exception as exc:
            report.append({"category": cat_name, "error": str(exc)})
            failed_urls += 1
            continue

        qa_links = parse_qa_links(cat_url, cat_html)
        qa_entries = []
        for q_title, q_url, q_date in qa_links:
            try:
                d_html = fetch_html(q_url)
                body = parse_qa_body(d_html)
                if len(body) >= 20:
                    qa_entries.append({"title": q_title, "url": q_url, "date": q_date, "body": body})
                time.sleep(0.08)
            except Exception:
                failed_urls += 1

        if qa_entries:
            doc_id, cnt = upsert_qa_doc(conn, cat_name, cat_url, qa_entries)
            conn.commit()
            synced_docs += 1
            synced_qas += cnt
            report.append({"category": cat_name, "doc_id": doc_id, "qa_count": cnt})

    conn.close()
    print(
        json.dumps(
            {
                "categories_found": len(cats),
                "synced_docs": synced_docs,
                "synced_qas": synced_qas,
                "failed_urls": failed_urls,
                "details": report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
