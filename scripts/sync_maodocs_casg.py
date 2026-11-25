#!/usr/bin/env python3
"""
从 MaoDocs（审计文库）https://docs.maoyanqing.com/accounting/ent/casg/
全量抓取《企业会计准则应用指南汇编2024》（财政部会计司编写组，2024年3月第1版）
全部 42 章并幂等写入 finlex.db（零第三方依赖，需 Python 3.9+）。

功能：
1. 自动解析目录页全部 42 章链接与章节名；
2. 清洗页面导航/页脚杂项，保留完整正文、例题、分录及表格文本，按二级标题（<h2> 一、二、三...）切分条文；
3. 幂等映射入库：
   - 已有 2006 旧版分则指南（财会〔2006〕18号）就地升级为 2024 汇编版（status='in_force'），并自动迁移保留原有 article_links；
   - 缺失分则指南（如基本准则、CAS 6/25/26/29/32/36/37/39/40/41/42 等）自动新增并建立与对应准则的关联边；
4. 发布单位统一标注为「财政部会计司」，source_name='MaoDocs（审计文库）'，source_url 为对应章节直达链接，
   供前端仅在完整文章底部展示信息来源备注（列表卡片不展示）。
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
BASE_URL = "https://docs.maoyanqing.com/accounting/ent/casg/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 文件名 -> (规范标题, 对应准则编号(None表示基本准则或旧版原保险), 现有旧版匹配关键字)
FILENAME_META: dict[str, tuple[str, int | None]] = {
    "00.html": ("企业会计准则——基本准则应用指南", 0),
    "01.html": ("企业会计准则第01号——存货应用指南", 1),
    "02.html": ("企业会计准则第02号——长期股权投资应用指南", 2),
    "03.html": ("企业会计准则第03号——投资性房地产应用指南", 3),
    "04.html": ("企业会计准则第04号——固定资产应用指南", 4),
    "05.html": ("企业会计准则第05号——生物资产应用指南", 5),
    "06.html": ("企业会计准则第06号——无形资产应用指南", 6),
    "07.html": ("企业会计准则第07号——非货币性资产交换应用指南", 7),
    "08.html": ("企业会计准则第08号——资产减值应用指南", 8),
    "09.html": ("企业会计准则第09号——职工薪酬应用指南", 9),
    "10.html": ("企业会计准则第10号——企业年金基金应用指南", 10),
    "11.html": ("企业会计准则第11号——股份支付应用指南", 11),
    "12.html": ("企业会计准则第12号——债务重组应用指南", 12),
    "13.html": ("企业会计准则第13号——或有事项应用指南", 13),
    "14.html": ("企业会计准则第14号——收入应用指南", 14),
    "16.html": ("企业会计准则第16号——政府补助应用指南", 16),
    "17.html": ("企业会计准则第17号——借款费用应用指南", 17),
    "18.html": ("企业会计准则第18号——所得税应用指南", 18),
    "19.html": ("企业会计准则第19号——外币折算应用指南", 19),
    "20.html": ("企业会计准则第20号——企业合并应用指南", 20),
    "21.html": ("企业会计准则第21号——租赁应用指南", 21),
    "22.html": ("企业会计准则第22号——金融工具确认和计量应用指南", 22),
    "23.html": ("企业会计准则第23号——金融资产转移应用指南", 23),
    "24.html": ("企业会计准则第24号——套期会计应用指南", 24),
    "25.html": ("企业会计准则第25号——保险合同应用指南", 25),
    "25b.html": ("企业会计准则第25号——原保险合同应用指南", None),
    "26.html": ("企业会计准则第26号——再保险合同应用指南", 26),
    "27.html": ("企业会计准则第27号——石油天然气开采应用指南", 27),
    "28.html": ("企业会计准则第28号——会计政策、会计估计变更和差错更正应用指南", 28),
    "29.html": ("企业会计准则第29号——资产负债表日后事项应用指南", 29),
    "30.html": ("企业会计准则第30号——财务报表列报应用指南", 30),
    "31.html": ("企业会计准则第31号——现金流量表应用指南", 31),
    "32.html": ("企业会计准则第32号——中期财务报告应用指南", 32),
    "33.html": ("企业会计准则第33号——合并财务报表应用指南", 33),
    "34.html": ("企业会计准则第34号——每股收益应用指南", 34),
    "35.html": ("企业会计准则第35号——分部报告应用指南", 35),
    "36.html": ("企业会计准则第36号——关联方披露应用指南", 36),
    "37.html": ("企业会计准则第37号——金融工具列报应用指南", 37),
    "39.html": ("企业会计准则第39号——公允价值计量应用指南", 39),
    "40.html": ("企业会计准则第40号——合营安排应用指南", 40),
    "41.html": ("企业会计准则第41号——在其他主体中权益的披露应用指南", 41),
    "42.html": ("企业会计准则第42号——持有待售的非流动资产、处置组和终止经营应用指南", 42),
}


def fetch_html(url: str, timeout: int = 25) -> str:
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def format_table(match: re.Match) -> str:
    """将 HTML <table> 转为紧凑可读的纯文本表格行。"""
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
    # 剔除脚本、样式、标题锚点 #、页脚导航
    fragment = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<a[^>]+class=[\"'][^\"']*header-anchor[^\"']*[\"'][^>]*>.*?</a>", "", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<table[^>]*>.*?</table>", format_table, fragment, flags=re.I | re.S)
    fragment = re.sub(r"</?(p|div|br|li|h[1-6]|blockquote|pre)[^>]*>", "\n", fragment, flags=re.I)
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html_lib.unescape(text)
    lines: list[str] = []
    for raw_ln in text.splitlines():
        ln = re.sub(r"[\t\r\u00a0]+", " ", raw_ln).strip()
        # 过滤站点底部固定提示与翻页残留
        if not ln or ln in ("#", "上一页", "下一页", "目录"):
            continue
        if ln.startswith("说明：本资料来源于互联网") or ln.startswith("© 202"):
            continue
        lines.append(ln)
    return "\n".join(lines)


def parse_toc(index_html: str) -> list[tuple[str, str, str]]:
    """返回 [(filename, url, chapter_label), ...]"""
    m_main = re.search(r"<main[^>]*>(.*?)</main>", index_html, re.I | re.S)
    body = m_main.group(1) if m_main else index_html
    items: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for href, txt in re.findall(r"<a[^>]+href=[\"']([^\"']*?casg/[^\"']+\.html)[\"'][^>]*>(.*?)</a>", body, re.I | re.S):
        url = urllib.parse.urljoin(BASE_URL, href.strip())
        fname = url.split("/")[-1]
        label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html_lib.unescape(txt))).strip()
        if fname not in seen and label:
            seen.add(fname)
            items.append((fname, url, label))
    return items


def parse_chapter_sections(page_html: str) -> list[tuple[str, str, str]]:
    """将章节 HTML 按 <h2> 切分为 [(article_no, heading, text_raw), ...]。"""
    m_main = re.search(r"<main[^>]*>(.*?)</main>", page_html, re.I | re.S)
    main_html = m_main.group(1) if m_main else page_html

    # 截断页脚元信息区域（page-meta / page-nav / vp-page-nav / footer）
    for cut_pat in (
        r"<footer\b",
        r"<div[^>]+class=[\"'][^\"']*(?:page-meta|page-nav|vp-page-nav|vp-page-meta)[^\"']*[\"']",
    ):
        mc = re.search(cut_pat, main_html, re.I)
        if mc:
            main_html = main_html[: mc.start()]

    # 移除 h1 及其之前的面包屑/元信息栏
    m_h1 = re.search(r"<h1[^>]*>.*?</h1>", main_html, re.I | re.S)
    if m_h1:
        main_html = main_html[m_h1.end() :]

    # 按 <h2> 切分
    h2_matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", main_html, re.I | re.S))
    sections: list[tuple[str, str, str]] = []

    if not h2_matches:
        txt = html_to_clean_text(main_html)
        if txt:
            sections.append(("全文", "应用指南正文", txt))
        return sections

    # 导语（h1 之后、第一个 h2 之前，若字数 >= 30）
    intro_txt = html_to_clean_text(main_html[: h2_matches[0].start()])
    if len(intro_txt) >= 30 and not intro_txt.startswith("最近更新"):
        sections.append(("导语", "章节概述", intro_txt))

    for i, m in enumerate(h2_matches):
        raw_h2 = re.sub(r"<a[^>]+class=[\"'][^\"']*header-anchor[^\"']*[\"'][^>]*>.*?</a>", "", m.group(1), flags=re.I | re.S)
        h2_title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html_lib.unescape(raw_h2))).strip().lstrip("#").strip()
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(main_html)
        sec_txt = html_to_clean_text(main_html[start:end])
        if not sec_txt:
            continue

        # 提取节号作为 article_no，如「一、总体要求」-> art_no='一', heading='总体要求'
        m_no = re.match(r"^([一二三四五六七八九十百]+)[、.．\s]+(.+)$", h2_title)
        if m_no:
            art_no = f"第{m_no.group(1)}部分"
            heading = m_no.group(2).strip()[:120]
        else:
            art_no = f"第{i + 1}节"
            heading = h2_title[:120]
        sections.append((art_no, heading, sec_txt))

    # 防止重复 article_no 触发 UNIQUE (document_id, article_no)
    used_nos: set[str] = set()
    deduped: list[tuple[str, str, str]] = []
    for idx, (ano, hd, txt) in enumerate(sections):
        final_no = ano
        k = 2
        while final_no in used_nos:
            final_no = f"{ano}({k})"
            k += 1
        used_nos.add(final_no)
        deduped.append((final_no, hd, txt))
    return deduped


def find_existing_guide(cur: sqlite3.Cursor, title: str, cas_num: int | None) -> int | None:
    row = cur.execute("SELECT id FROM documents WHERE title=?", (title,)).fetchone()
    if row:
        return row[0]
    if cas_num is not None and cas_num > 0:
        # 兼容如「第24号——套期保值应用指南」升级为「第24号——套期会计应用指南」
        pat = f"企业会计准则第{cas_num:02d}号——%应用指南"
        row = cur.execute("SELECT id FROM documents WHERE title LIKE ?", (pat,)).fetchone()
        if row:
            return row[0]
    return None


def find_matching_standard_first_article(cur: sqlite3.Cursor, cas_num: int | None) -> int | None:
    if cas_num is None:
        return None
    if cas_num == 0:
        row = cur.execute(
            "SELECT id FROM documents WHERE domain='accounting' AND doc_type='standard' AND title LIKE '%基本准则%' ORDER BY id ASC LIMIT 1"
        ).fetchone()
    else:
        row = cur.execute(
            "SELECT id FROM documents WHERE domain='accounting' AND doc_type='standard' AND title LIKE ? ORDER BY id DESC LIMIT 1",
            (f"企业会计准则第{cas_num:02d}号——%",),
        ).fetchone()
    if not row:
        return None
    art = cur.execute("SELECT id FROM articles WHERE document_id=? ORDER BY seq ASC, id ASC LIMIT 1", (row[0],)).fetchone()
    return art[0] if art else None


def upsert_guide(
    conn: sqlite3.Connection,
    fname: str,
    chapter_label: str,
    url: str,
    sections: list[tuple[str, str, str]],
) -> tuple[int, str, int]:
    cur = conn.cursor()
    if fname in FILENAME_META:
        title, cas_num = FILENAME_META[fname]
    else:
        title = f"企业会计准则应用指南——{chapter_label}"
        cas_num = None

    total_chars = sum(len(s[2]) for s in sections)
    doc_no = "《企业会计准则应用指南汇编2024》"
    pub_date = "2024-03-01"
    eff_date = "2024-03-01"
    summary = f"《企业会计准则应用指南汇编2024》（财政部会计司编写组，2024年3月第1版）{chapter_label}，共 {len(sections)} 个章节（约 {total_chars:,} 字），涵盖会计科目、账务处理、例题与衔接规定。"

    existing_id = find_existing_guide(cur, title, cas_num)
    preserved_links: list[tuple[str, int, str, str | None, str, str]] = []

    if existing_id is not None:
        doc_id = existing_id
        action = "updated"
        old_art_ids = [r[0] for r in cur.execute("SELECT id FROM articles WHERE document_id=?", (doc_id,)).fetchall()]
        if old_art_ids:
            placeholders = ",".join("?" * len(old_art_ids))
            old_set = set(old_art_ids)
            for lr in cur.execute(
                f"SELECT from_article_id, to_article_id, link_type, note, strength, rel_kind FROM article_links "
                f"WHERE from_article_id IN ({placeholders}) OR to_article_id IN ({placeholders})",
                old_art_ids + old_art_ids,
            ).fetchall():
                f_id, t_id, ltype, note, strength, rkind = lr
                if f_id in old_set and t_id not in old_set:
                    preserved_links.append(("out", t_id, ltype, note, strength, rkind))
                elif t_id in old_set and f_id not in old_set:
                    preserved_links.append(("in", f_id, ltype, note, strength, rkind))
            cur.execute(
                f"DELETE FROM article_links WHERE from_article_id IN ({placeholders}) OR to_article_id IN ({placeholders})",
                old_art_ids + old_art_ids,
            )
            cur.execute("DELETE FROM articles WHERE document_id=?", (doc_id,))

        cur.execute(
            """
            UPDATE documents
            SET title=?, doc_no=?, issuer='财政部会计司', pub_date=?, effective_date=?,
                status='in_force', source_name='MaoDocs（审计文库）', source_url=?,
                summary=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (title, doc_no, pub_date, eff_date, url, summary, doc_id),
        )
    else:
        action = "inserted"
        cur.execute(
            """
            INSERT INTO documents (
                doc_type, domain, title, doc_no, issuer, pub_date, effective_date,
                status, source_name, source_url, summary
            ) VALUES ('guidance', 'accounting', ?, ?, '财政部会计司', ?, ?, 'in_force', 'MaoDocs（审计文库）', ?, ?)
            """,
            (title, doc_no, pub_date, eff_date, url, summary),
        )
        doc_id = cur.lastrowid

    new_first_art_id = None
    for idx, (art_no, heading, text_raw) in enumerate(sections):
        cur.execute(
            "INSERT INTO articles (document_id, article_no, heading, text_raw, seq) VALUES (?, ?, ?, ?, ?)",
            (doc_id, art_no, heading, text_raw, idx),
        )
        if new_first_art_id is None:
            new_first_art_id = cur.lastrowid

    # 恢复原有 article_links
    if new_first_art_id is not None:
        for direction, other_art_id, ltype, note, strength, rkind in preserved_links:
            f_id = new_first_art_id if direction == "out" else other_art_id
            t_id = other_art_id if direction == "out" else new_first_art_id
            cur.execute(
                "INSERT OR IGNORE INTO article_links (from_article_id, to_article_id, link_type, note, strength, rel_kind) VALUES (?, ?, ?, ?, ?, ?)",
                (f_id, t_id, ltype, note, strength, rkind),
            )
        # 为新增指南自动建立与对应准则的关联边
        if action == "inserted":
            std_art_id = find_matching_standard_first_article(cur, cas_num)
            if std_art_id is not None:
                cur.execute(
                    "INSERT OR IGNORE INTO article_links (from_article_id, to_article_id, link_type, note, strength, rel_kind) VALUES (?, ?, 'guidance', '对应准则应用指南（2024汇编版）', 'strong', 'thematic')",
                    (std_art_id, new_first_art_id),
                )

    return doc_id, action, len(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description="全量同步 MaoDocs《企业会计准则应用指南汇编2024》至 finlex.db")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--limit", type=int, default=0, help="仅抓取前 N 章（0 为全部 42 章）")
    args = parser.parse_args()

    toc_html = fetch_html(BASE_URL)
    chapters = parse_toc(toc_html)
    if args.limit > 0:
        chapters = chapters[: args.limit]

    conn = sqlite3.connect(str(args.db))
    updated = 0
    inserted = 0
    failed = 0
    total_sections = 0
    total_chars = 0
    details = []

    for fname, url, label in chapters:
        try:
            page_html = fetch_html(url)
            sections = parse_chapter_sections(page_html)
            if not sections:
                failed += 1
                details.append({"file": fname, "label": label, "error": "empty_sections"})
                continue
            doc_id, action, sec_cnt = upsert_guide(conn, fname, label, url, sections)
            conn.commit()
            chars = sum(len(s[2]) for s in sections)
            total_sections += sec_cnt
            total_chars += chars
            if action == "updated":
                updated += 1
            else:
                inserted += 1
            details.append({"file": fname, "doc_id": doc_id, "action": action, "sections": sec_cnt, "chars": chars})
            time.sleep(0.06)
        except Exception as exc:
            failed += 1
            details.append({"file": fname, "label": label, "error": str(exc)})

    conn.close()
    print(
        json.dumps(
            {
                "chapters_found": len(chapters),
                "updated": updated,
                "inserted": inserted,
                "failed": failed,
                "total_sections": total_sections,
                "total_chars": total_chars,
                "details": details,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
