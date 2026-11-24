#!/usr/bin/env python3
"""
FinLex 静态站点（site/ PWA）与数据校验脚本（零第三方依赖，需 Python 3.9+）

检查项：
1. PWA 必备静态资源齐全（index.html / manifest.webmanifest / sw.js / icon.svg / icon-192.png / icon-512.png）；
2. data/index.js 与 data/fulltext.js 结构合法，全部文档对应 data/docs/doc_<id>.js 分片齐全；
3. 悬空关联边为 0；
4. 案例摘要与非规范依据标识合规；
5. 全站文本（HTML/JS/JSON）零本机路径隐私泄漏。
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
    "manifest.webmanifest",
    "sw.js",
    "icon.svg",
    "icon-192.png",
    "icon-512.png",
    "data/index.js",
    "data/fulltext.js",
]


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
    doc_ids = {d["id"] for d in docs}

    # 校验每份文档的分片文件存在且案例摘要合规
    missing_shards = 0
    for d in docs:
        shard = SITE_DIR / "data" / "docs" / f"doc_{d['id']}.js"
        if not shard.exists():
            missing_shards += 1
        if d.get("doc_type") == "case":
            if not d.get("is_case"):
                errors.append(f"案例 doc_id={d['id']} 缺少 is_case=true 标识")
            if len((d.get("summary") or "").strip()) < 20:
                warnings.append(f"案例 doc_id={d['id']} 摘要少于 20 字")
    if missing_shards:
        errors.append(f"缺少 {missing_shards} 份文档分片文件（site/data/docs/doc_*.js）")

    # 校验悬空关联边
    dangling = sum(1 for e in links if e["from_doc_id"] not in doc_ids or e["to_doc_id"] not in doc_ids)
    if dangling:
        errors.append(f"检测到 {dangling} 条悬空关联边")

    # 校验 fulltext.js
    ft_rows = parse_js_json(SITE_DIR / "data" / "fulltext.js", "window.__finlexFulltextLoaded(", ");")
    if not isinstance(ft_rows, list) or len(ft_rows) == 0:
        errors.append("site/data/fulltext.js 为空或格式非法")

    # 隐私扫描（扫描 HTML / manifest / sw / index.js / fulltext.js 及抽样或全量 docs）
    privacy_leaks = 0
    scan_targets = [
        SITE_DIR / "index.html",
        SITE_DIR / "manifest.webmanifest",
        SITE_DIR / "sw.js",
        SITE_DIR / "data" / "index.js",
        SITE_DIR / "data" / "fulltext.js",
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
        "articles_in_fulltext": len(ft_rows),
        "doc_links": len(links),
        "missing_shards": missing_shards,
        "dangling_links": dangling,
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
