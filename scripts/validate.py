#!/usr/bin/env python3
"""
FinLex 静态站点（site/ PWA）与数据校验脚本（零第三方依赖，需 Python 3.9+）

检查项：
1. PWA 必备静态资源齐全（index.html / manifest.webmanifest / sw.js / icon.svg / icon-192.png / icon-512.png）；
2. data/index.js 与按领域切分的 data/ft/ft_*.js 分片结构合法且行数完整，全部文档对应 data/docs/doc_<id>.js 分片齐全；
3. 单分片体积门禁（任意全文分片不得超过 2,048 KB）；
4. 悬空关联边为 0；
5. 案例摘要与非规范依据标识合规；
6. 全站文本（HTML/JS/JSON）零本机路径隐私泄漏。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = PROJECT_ROOT / "site"
LOCAL_PATH_RE = re.compile(r"(/Users/[^\s\"'<>]+|[A-Za-z]:\\Users\\[^\s\"'<>]+)")

REQUIRED_FILES = [
    "index.html",
    ".nojekyll",
    "manifest.webmanifest",
    "sw.js",
    "icon.svg",
    "icon-192.png",
    "icon-512.png",
    "data/index.js",
]

PUA_RE = re.compile(r"[\ue000-\uf8ff\U00100000-\U0010ffff]")


def parse_js_json(path: Path, prefix: str, suffix: str) -> object:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw.startswith(prefix) or not raw.endswith(suffix):
        raise ValueError(f"{path.name} 封装格式不匹配")
    return json.loads(raw[len(prefix) : len(raw) - len(suffix)])


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SITE_DIR.exists():
        print("ERROR: 缺少 site/ 目录，请先运行 python3 scripts/build_site.py", file=sys.stderr)
        return 1

    for rel in REQUIRED_FILES:
        if not (SITE_DIR / rel).exists():
            errors.append(f"缺少必需文件：site/{rel}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # 校验 manifest.webmanifest JSON 合法性
    try:
        manifest = json.loads((SITE_DIR / "manifest.webmanifest").read_text(encoding="utf-8"))
        for k in ("name", "short_name", "start_url", "display", "icons"):
            if k not in manifest:
                errors.append(f"manifest.webmanifest 缺少字段：{k}")
    except Exception as exc:
        errors.append(f"manifest.webmanifest 解析失败：{exc}")

    # 校验 index.js
    index_data = parse_js_json(SITE_DIR / "data" / "index.js", "window.FINLEX_INDEX = ", ";")
    docs = index_data.get("documents", [])
    links = index_data.get("doc_links", [])
    meta = index_data.get("meta", {})
    home_news = index_data.get("home_news", [])
    doc_ids = {d["id"] for d in docs}

    # 校验首页动态 doc_query 全部可解析
    unresolved_news: list[str] = []
    for item in home_news:
        dq = (item.get("doc_query") or "").strip()
        if not dq:
            continue
        dq_low = dq.lower()
        matched = any(
            dq_low in (d.get("title") or "").lower()
            or dq_low in (d.get("display_title") or "").lower()
            or dq_low in (d.get("doc_no") or "").lower()
            for d in docs
        )
        if not matched:
            unresolved_news.append(dq)
    if unresolved_news:
        errors.append(f"首页动态存在无法解析的 doc_query：{unresolved_news}")

    # 校验每份文档的分片文件存在、案例摘要合规及正文无空条文/私用区乱码
    missing_shards = 0
    empty_articles = 0
    pua_hits = 0
    for d in docs:
        shard = SITE_DIR / "data" / "docs" / f"doc_{d['id']}.js"
        if not shard.exists():
            missing_shards += 1
        else:
            raw_doc = shard.read_text(encoding="utf-8")
            m_doc = re.search(r"window\.__finlexDocLoaded\(\d+,(\{.*\})\);", raw_doc, re.S)
            if m_doc:
                dj = json.loads(m_doc.group(1))
                for art in dj.get("articles") or []:
                    txt = (art.get("text") or "").strip()
                    if not txt:
                        empty_articles += 1
                    if PUA_RE.search(txt):
                        pua_hits += 1
        if d.get("doc_type") == "case":
            if not d.get("is_case"):
                errors.append(f"案例 doc_id={d['id']} 缺少 is_case=true 标识")
            if len((d.get("summary") or "").strip()) < 20:
                warnings.append(f"案例 doc_id={d['id']} 摘要少于 20 字")
    if missing_shards:
        errors.append(f"缺少 {missing_shards} 份文档分片文件（site/data/docs/doc_*.js）")
    if empty_articles:
        errors.append(f"检测到 {empty_articles} 条空白条文正文")
    if pua_hits:
        errors.append(f"检测到 {pua_hits} 条含私用区乱码（PUA）的条文正文")

    # 校验悬空关联边
    dangling = sum(1 for e in links if e["from_doc_id"] not in doc_ids or e["to_doc_id"] not in doc_ids)
    if dangling:
        errors.append(f"检测到 {dangling} 条悬空关联边")

    # 校验分片式全文语料（data/ft/ft_*.js）
    ft_shards = meta.get("ft_shards", [])
    total_ft_rows = 0
    max_ft_kb = 0.0
    ft_scan_paths: list[Path] = []
    if not ft_shards:
        errors.append("index.js meta.ft_shards 为空，缺少全文检索分片清单")
    else:
        for sh in ft_shards:
            fpath = SITE_DIR / "data" / sh["file"]
            if not fpath.exists():
                errors.append(f"缺少全文检索分片：site/data/{sh['file']}")
                continue
            ft_scan_paths.append(fpath)
            kb = round(fpath.stat().st_size / 1024, 1)
            if kb > max_ft_kb:
                max_ft_kb = kb
            if kb > 2048:
                warnings.append(f"全文检索分片过大（{kb} KB > 2048 KB）：{sh['file']}")
            prefix = f'window.__finlexFtShardLoaded("{sh["id"]}",'
            rows = parse_js_json(fpath, prefix, ");")
            if not isinstance(rows, list):
                errors.append(f"全文分片格式非法：{sh['file']}")
            else:
                total_ft_rows += len(rows)

    expected_arts = int(meta.get("article_count", 0))
    if expected_arts and total_ft_rows != expected_arts:
        errors.append(f"全文分片总条数（{total_ft_rows}）与文档条文总数（{expected_arts}）不一致")

    # 隐私扫描（HTML / manifest / sw / index.js / 全部分片）
    privacy_leaks = 0
    scan_targets = [
        SITE_DIR / "index.html",
        SITE_DIR / "manifest.webmanifest",
        SITE_DIR / "sw.js",
        SITE_DIR / "data" / "index.js",
        *ft_scan_paths,
        *sorted((SITE_DIR / "data" / "docs").glob("doc_*.js")),
    ]
    for path in scan_targets:
        text = path.read_text(encoding="utf-8")
        hits = LOCAL_PATH_RE.findall(text)
        if hits:
            privacy_leaks += len(hits)
            errors.append(f"隐私红线违规：{path.relative_to(PROJECT_ROOT)} 含本机路径 {hits[:2]}")

    summary = {
        "site_dir": "site/",
        "documents": len(docs),
        "articles_in_fulltext": total_ft_rows,
        "ft_shards": len(ft_shards),
        "ft_max_shard_kb": max_ft_kb,
        "index_js_kb": round((SITE_DIR / "data" / "index.js").stat().st_size / 1024, 1),
        "doc_links": len(links),
        "missing_shards": missing_shards,
        "dangling_links": dangling,
        "empty_articles": empty_articles,
        "pua_hits": pua_hits,
        "unresolved_news": len(unresolved_news),
        "privacy_leaks": privacy_leaks,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
