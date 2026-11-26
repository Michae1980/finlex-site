#!/usr/bin/env python3
"""
FinLex 正式静态站点（site/ PWA）构建脚本（零第三方依赖，需 Python 3.9+）

用法：
- 本地全量同步与构建（自动检测 ../finlex/backend/data/finlex.db）：
    python3 scripts/build_site.py
- GitHub Actions CI 构建（不依赖外部 finlex.db，基于仓库内已提交的脱敏分片数据重建 site/ HTML 与 PWA 资产）：
    python3 scripts/build_site.py --ci
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
import zlib
from pathlib import Path

from build_prototype import DEFAULT_DB, PROJECT_ROOT, PROTOTYPE_DIR, build_from_db

PWA_SRC_DIR = PROTOTYPE_DIR / "pwa"
SITE_DIR = PROJECT_ROOT / "site"
TEMPLATE_PATH = PROTOTYPE_DIR / "template.html"


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", crc)


def generate_pwa_png(path: Path, size: int) -> None:
    """零依赖生成圆角渐变 FinLex PWA 图标（icon-192.png / icon-512.png）。"""
    rows = []
    radius = size * 0.22
    left_x1, left_x2 = int(size * 0.17), int(size * 0.48)
    left_y1, left_y2 = int(size * 0.21), int(size * 0.79)
    right_x1, right_x2 = int(size * 0.53), int(size * 0.83)
    top_y1, top_y2 = int(size * 0.21), int(size * 0.47)
    bot_y1, bot_y2 = int(size * 0.53), int(size * 0.79)

    for y in range(size):
        row = bytearray([0])  # filter type 0
        t_y = y / max(1, size - 1)
        for x in range(size):
            # 圆角透明裁切
            dx = max(radius - x, 0.0, x - (size - 1 - radius))
            dy = max(radius - y, 0.0, y - (size - 1 - radius))
            if dx * dx + dy * dy > radius * radius:
                row.extend((0, 0, 0, 0))
                continue
            t = 0.5 * (x / max(1, size - 1) + t_y)
            r = int(30 + (37 - 30) * t)
            g = int(58 + (99 - 58) * t)
            b = int(138 + (235 - 138) * t)
            a = 255
            # 左侧半透明目录面板
            if left_x1 <= x <= left_x2 and left_y1 <= y <= left_y2:
                r = int(r * 0.78 + 255 * 0.22)
                g = int(g * 0.78 + 255 * 0.22)
                b = int(b * 0.78 + 255 * 0.22)
            # 右上主原文卡片（纯白）
            elif right_x1 <= x <= right_x2 and top_y1 <= y <= top_y2:
                r, g, b = 248, 250, 252
            # 右下关联图谱卡片（浅蓝）
            elif right_x1 <= x <= right_x2 and bot_y1 <= y <= bot_y2:
                r, g, b = 147, 197, 253
            row.extend((r, g, b, a))
        rows.append(bytes(row))

    raw = b"".join(rows)
    ihdr = struct.pack("!IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, level=6))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def ensure_pwa_icons() -> None:
    PWA_SRC_DIR.mkdir(parents=True, exist_ok=True)
    for sz in (192, 512):
        icon_path = PWA_SRC_DIR / f"icon-{sz}.png"
        if not icon_path.exists():
            generate_pwa_png(icon_path, sz)


def copy_tree_clean(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 FinLex 正式静态站点（site/ PWA）")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="本地 finlex.db 路径")
    parser.add_argument("--ci", action="store_true", help="CI 模式：仅使用仓库内已有脱敏数据重建 site/ 模板与 PWA 资源")
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="方案 B（本机私用模式）：叠加 intl_data/private/*.json 并输出至 git-ignored 的 site_private/，不污染公开 site/",
    )
    args = parser.parse_args()

    ensure_pwa_icons()
    if args.include_private:
        private_site_dir = PROJECT_ROOT / "site_private"
        private_site_dir.mkdir(parents=True, exist_ok=True)
        db_stats = build_from_db(args.db, include_private=True, out_root=private_site_dir)
        pwa_files = ["manifest.webmanifest", "sw.js", "icon.svg", "icon-192.png", "icon-512.png"]
        for fname in pwa_files:
            src = PWA_SRC_DIR / fname
            if src.exists():
                shutil.copy2(src, private_site_dir / fname)
        print(
            json.dumps(
                {
                    "mode": "private_local",
                    "site_dir": "site_private/",
                    "pwa_assets": pwa_files,
                    "db_sync_stats": {
                        "documents": db_stats["documents"],
                        "articles": db_stats["articles"],
                        "doc_links": db_stats["doc_links"],
                        "index_js_kb": db_stats["index_js_kb"],
                        "ft_shards": db_stats["ft_shards"],
                        "ft_total_kb": db_stats["ft_total_kb"],
                        "ft_max_shard_kb": db_stats["ft_max_shard_kb"],
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    SITE_DIR.mkdir(parents=True, exist_ok=True)

    db_stats = None
    if not args.ci and args.db.exists():
        db_stats = build_from_db(args.db)
        copy_tree_clean(PROTOTYPE_DIR / "data", SITE_DIR / "data")
    elif not (SITE_DIR / "data" / "index.js").exists():
        if (PROTOTYPE_DIR / "data" / "index.js").exists():
            copy_tree_clean(PROTOTYPE_DIR / "data", SITE_DIR / "data")
        else:
            print("ERROR: 未找到 site/data/index.js 或 finlex.db，无法构建静态站点。", file=sys.stderr)
            return 1

    # 同步 HTML 与 PWA 静态资产到 site/ 和 prototype/
    html_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    (SITE_DIR / "index.html").write_text(html_text, encoding="utf-8")
    (PROTOTYPE_DIR / "index.html").write_text(html_text, encoding="utf-8")

    pwa_files = ["manifest.webmanifest", "sw.js", "icon.svg", "icon-192.png", "icon-512.png"]
    for fname in pwa_files:
        src = PWA_SRC_DIR / fname
        if src.exists():
            shutil.copy2(src, SITE_DIR / fname)
            shutil.copy2(src, PROTOTYPE_DIR / fname)

    result = {
        "mode": "ci" if args.ci else ("db_sync" if db_stats else "cached_data"),
        "site_dir": "site/",
        "pwa_assets": pwa_files,
        "db_sync_stats": {
            "documents": db_stats["documents"],
            "articles": db_stats["articles"],
            "doc_links": db_stats["doc_links"],
            "index_js_kb": db_stats["index_js_kb"],
            "ft_shards": db_stats["ft_shards"],
            "ft_total_kb": db_stats["ft_total_kb"],
            "ft_max_shard_kb": db_stats["ft_max_shard_kb"],
        }
        if db_stats
        else None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
