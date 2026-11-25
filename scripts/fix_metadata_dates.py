#!/usr/bin/env python3
"""
批量修复 finlex.db 中 40 份文档的发布日期、生效日期与缺失文号（幂等脚本）。
全部日期与文号均核对自财政部（mof.gov.cn / kjs.mof.gov.cn）、证监会（csrc.gov.cn）与中注协（cicpa.org.cn）官方页面。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT.parent / "finlex" / "backend" / "data" / "finlex.db"

# (doc_id, pub_date, effective_date, doc_no_or_none_to_keep)
VERIFIED_UPDATES: list[tuple[int, str, str, str | None]] = [
    # 6 份会计准则与准则解释
    (3, "2014-03-27", "2014-07-01", "财会〔2014〕14号"),
    (10, "2014-01-27", "2014-07-01", "财会〔2014〕8号"),
    (16, "2017-05-10", "2017-06-12", "财会〔2017〕15号"),
    (29, "2014-01-26", "2014-07-01", "财会〔2014〕7号"),
    (33, "2014-02-17", "2014-07-01", "财会〔2014〕10号"),
    (49, "2022-11-30", "2022-11-30", "财会〔2022〕31号"),
    # 8 份可持续披露准则与证监会/财政部监管文件
    (121, "2025-09-12", "2025-09-12", None),
    (122, "2024-12-16", "2024-12-16", None),
    (123, "2025-12-25", "2025-12-25", None),
    (124, "2025-04-14", "2025-04-14", None),
    (125, "2019-12-23", "2019-12-23", None),
    (126, "2026-01-27", "2026-01-27", None),
    (127, "2021-03-09", "2021-03-09", None),
    (128, "2023-08-23", "2023-08-23", None),
    # 19 份中注协审计准则问题解答（核自 cicpa.org.cn 问题解答目录）
    (129, "2014-12-31", "2014-12-31", None),  # 第10号
    (130, "2014-12-31", "2014-12-31", None),  # 第11号
    (131, "2019-12-31", "2019-12-31", None),  # 第12号（2019修订）
    (132, "2014-12-31", "2014-12-31", None),  # 第13号
    (133, "2018-04-15", "2018-04-15", None),  # 第14号
    (134, "2018-04-15", "2018-04-15", None),  # 第15号
    (135, "2021-02-02", "2021-02-02", None),  # 第16号
    (136, "2024-01-29", "2024-01-29", None),  # 第17号
    (137, "2025-01-23", "2025-01-23", None),  # 第18号
    (138, "2025-01-23", "2025-01-23", None),  # 第19号
    (139, "2019-12-31", "2019-12-31", None),  # 第1号（2019修订）
    (140, "2019-12-31", "2019-12-31", None),  # 第2号（2019修订）
    (141, "2013-10-31", "2013-10-31", None),  # 第3号
    (142, "2019-12-31", "2019-12-31", None),  # 第4号（2019修订）
    (143, "2013-10-31", "2013-10-31", None),  # 第5号
    (144, "2019-12-31", "2019-12-31", None),  # 第6号（2019修订）
    (145, "2014-12-31", "2014-12-31", None),  # 第7号
    (146, "2014-12-31", "2014-12-31", None),  # 第8号
    (147, "2014-12-31", "2014-12-31", None),  # 第9号
    # 7 份审计指引与财政部发布通知
    (152, "2025-12-30", "2025-12-30", None),
    (153, "2025-05-16", "2025-05-16", None),
    (156, "2025-01-20", "2025-01-20", "财会〔2024〕29号"),
    (157, "2022-01-07", "2022-01-07", "财会〔2022〕1号"),
    (158, "2020-12-02", "2020-12-02", "财会〔2020〕17号"),
    (159, "2023-01-03", "2023-01-03", "财会〔2022〕36号"),
    (160, "2024-05-24", "2024-05-24", None),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="批量修复 finlex.db 元数据日期与文号")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    conn = sqlite3.connect(str(args.db))
    cur = conn.cursor()
    updated = 0
    for doc_id, pub_date, eff_date, doc_no in VERIFIED_UPDATES:
        if doc_no is not None:
            cur.execute(
                "UPDATE documents SET pub_date=?, effective_date=?, doc_no=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (pub_date, eff_date, doc_no, doc_id),
            )
        else:
            cur.execute(
                "UPDATE documents SET pub_date=?, effective_date=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (pub_date, eff_date, doc_id),
            )
        updated += cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"updated_docs": updated, "expected": len(VERIFIED_UPDATES)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
