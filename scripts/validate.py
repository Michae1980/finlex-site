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
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"
INTL_SCHEMA_PATH = PROJECT_ROOT / "schema" / "intl-data.v1.schema.json"

VALID_INTL_FRAMEWORKS = {"INTL", "US"}
VALID_DOMAINS = {"accounting", "audit", "tax", "general"}
VALID_DOC_TYPES = {"law", "regulation", "standard", "rule", "guidance", "normative", "interpretation", "case"}
VALID_STATUSES = {"in_force", "will_replace", "upcoming", "outdated", "pending"}
VALID_SOURCE_KINDS = {"official", "third_party", "official_pending", "user_submitted"}
REQUIRED_INTL_DOC_KEYS = {
    "code",
    "framework",
    "domain",
    "doc_type",
    "title",
    "display_title",
    "series_badge",
    "doc_no",
    "issuer",
    "pub_date",
    "effective_date",
    "status",
    "version_level",
    "version_note",
    "source_name",
    "source_url",
    "source_kind",
    "summary",
    "cited_codes",
    "cas_links",
    "articles",
}
ALLOWED_INTL_DOC_KEYS = REQUIRED_INTL_DOC_KEYS | {"slug", "replaced_by_code", "ifrs_links"}


def validate_intl_data_packs(errors: list[str], warnings: list[str]) -> dict[str, int]:
    """零依赖校验 intl_data/*.json 是否符合 schema/intl-data.v1.schema.json 契约与全局 code 唯一性。"""
    if not INTL_SCHEMA_PATH.exists():
        errors.append("缺少 Schema 契约文件：schema/intl-data.v1.schema.json")
    else:
        try:
            json.loads(INTL_SCHEMA_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"schema/intl-data.v1.schema.json JSON 解析失败：{exc}")

    pack_count = 0
    doc_count = 0
    seen_codes: dict[str, str] = {}
    if not INTL_DATA_DIR.exists():
        return {"packs": 0, "docs": 0}

    for jf in sorted(INTL_DATA_DIR.glob("*.json")):
        if jf.name == "home_news.json":
            continue
        pack_count += 1
        try:
            pack = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"intl_data/{jf.name} JSON 解析失败：{exc}")
            continue
        docs = pack.get("documents")
        if not isinstance(docs, list) or not docs:
            errors.append(f"intl_data/{jf.name} 缺少非空 documents 数组")
            continue
        for idx, doc in enumerate(docs):
            doc_count += 1
            if not isinstance(doc, dict):
                errors.append(f"intl_data/{jf.name} documents[{idx}] 必须为对象")
                continue
            code = str(doc.get("code") or f"<idx:{idx}>")
            missing = REQUIRED_INTL_DOC_KEYS - set(doc.keys())
            extra = set(doc.keys()) - ALLOWED_INTL_DOC_KEYS
            if missing:
                errors.append(f"intl_data/{jf.name}[{code}] 缺少必填字段：{sorted(missing)}")
            if extra:
                errors.append(f"intl_data/{jf.name}[{code}] 含未定义字段：{sorted(extra)}")
            if code in seen_codes:
                errors.append(f"intl_data 全局 code 冲突：{code}（{seen_codes[code]} 与 {jf.name}）")
            else:
                seen_codes[code] = jf.name
            if doc.get("framework") not in VALID_INTL_FRAMEWORKS:
                errors.append(f"intl_data/{jf.name}[{code}] framework 非法：{doc.get('framework')}")
            if doc.get("domain") not in VALID_DOMAINS:
                errors.append(f"intl_data/{jf.name}[{code}] domain 非法：{doc.get('domain')}")
            if doc.get("doc_type") not in VALID_DOC_TYPES:
                errors.append(f"intl_data/{jf.name}[{code}] doc_type 非法：{doc.get('doc_type')}")
            if doc.get("status") not in VALID_STATUSES:
                errors.append(f"intl_data/{jf.name}[{code}] status 非法：{doc.get('status')}")
            if doc.get("source_kind") not in VALID_SOURCE_KINDS:
                errors.append(f"intl_data/{jf.name}[{code}] source_kind 非法：{doc.get('source_kind')}")
            surl = str(doc.get("source_url") or "")
            if not (surl.startswith("http://") or surl.startswith("https://")):
                errors.append(f"intl_data/{jf.name}[{code}] source_url 非法：{surl}")
            for lk_field in ("cas_links", "ifrs_links"):
                if lk_field in doc:
                    pairs = doc[lk_field]
                    if not isinstance(pairs, list) or any(
                        not isinstance(p, list) or len(p) != 2 or not all(isinstance(x, str) and x.strip() for x in p)
                        for p in pairs
                    ):
                        errors.append(f"intl_data/{jf.name}[{code}] {lk_field} 须为二元字符串数组")
            arts = doc.get("articles")
            if not isinstance(arts, list) or not arts:
                errors.append(f"intl_data/{jf.name}[{code}] articles 必须为非空数组")
            else:
                for a_idx, a in enumerate(arts):
                    if not isinstance(a, dict) or not (a.get("no") or "").strip() or not (a.get("text") or "").strip():
                        errors.append(f"intl_data/{jf.name}[{code}] articles[{a_idx}] 缺少非空 no 或 text")
    return {"packs": pack_count, "docs": doc_count}


def parse_js_json(path: Path, prefix: str, suffix: str) -> object:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw.startswith(prefix) or not raw.endswith(suffix):
        raise ValueError(f"{path.name} 封装格式不匹配")
    return json.loads(raw[len(prefix) : len(raw) - len(suffix)])


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    intl_schema_stats = validate_intl_data_packs(errors, warnings)

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

    # 校验悬空关联边与图谱连通性/跨体系映射巡检
    dangling = sum(1 for e in links if e["from_doc_id"] not in doc_ids or e["to_doc_id"] not in doc_ids)
    if dangling:
        errors.append(f"检测到 {dangling} 条悬空关联边")

    deg: dict[int, int] = {did: 0 for did in doc_ids}
    intl_map_deg: dict[int, int] = {did: 0 for did in doc_ids}
    for e in links:
        f_id, t_id = e["from_doc_id"], e["to_doc_id"]
        if f_id in deg:
            deg[f_id] += 1
        if t_id in deg:
            deg[t_id] += 1
        if e.get("rel_kind") == "intl_mapping":
            if f_id in intl_map_deg:
                intl_map_deg[f_id] += 1
            if t_id in intl_map_deg:
                intl_map_deg[t_id] += 1
    isolated_docs = sum(1 for did in doc_ids if deg[did] == 0)
    connected_docs = len(doc_ids) - isolated_docs
    unmapped_intl_us_standards = sum(
        1
        for d in docs
        if d.get("framework") in ("INTL", "US")
        and d.get("doc_type") == "standard"
        and intl_map_deg.get(d["id"], 0) == 0
    )

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
        "intl_schema_packs": intl_schema_stats["packs"],
        "intl_schema_docs": intl_schema_stats["docs"],
        "documents": len(docs),
        "connected_docs": connected_docs,
        "isolated_docs": isolated_docs,
        "unmapped_intl_us_standards": unmapped_intl_us_standards,
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
