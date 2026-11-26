#!/usr/bin/env python3
"""
方案 B：本机私用官方 PDF 全文解析导入工具（严格 git-ignored，绝不上传公开仓库）

使用步骤：
1. 在项目根目录新建 local_pdfs/ 文件夹（已加入 .gitignore）；
2. 将你通过个人免费 IFRS.org / IAASB / IESBA 账号下载的官方英文 PDF 放入 local_pdfs/，
   建议文件名包含标准编号（例如 IFRS_15.pdf、IAS_36.pdf、IFRS_18.pdf、ISA_315.pdf）；
3. 运行本脚本解析官方段落号（如 1–129、B1–B89、A1–A240）：
       python3 scripts/import_private_intl_pdfs.py
4. 运行私用离线构建命令，生成独立的本机离线站点 site_private/index.html（已加入 .gitignore，不污染公开 site/）：
       python3 scripts/build_site.py --include-private
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_PDF_DIR = PROJECT_ROOT / "local_pdfs"
PRIVATE_OUT_DIR = PROJECT_ROOT / "intl_data" / "private"

CODE_RE = re.compile(
    r"\b(IFRS\s*S?\d{1,2}|IAS\s*\d{1,2}|IFRIC\s*\d{1,2}|SIC[-\s]*\d{1,2}|ISQM\s*\d|ISA\s*\d{3}|ISRE\s*\d{4}|ISAE\s*\d{4}|ISSA\s*\d{4}|ISRS\s*\d{4})\b",
    re.IGNORECASE,
)

# 匹配 IFRS / IAS / ISA 官方段落号行首（如 "1 ", "31 ", "35A ", "B34 ", "BC12 ", "A42 ", "C1 "）
PARA_LINE_RE = re.compile(r"^((?:BC|IE|DO|AG|IG|B|C|A)?\d{1,3}[A-Z]?)\s+(.+)$")


def normalize_code(raw: str) -> str:
    s = re.sub(r"[_-]+", " ", raw).strip()
    m = CODE_RE.search(s)
    if not m:
        return ""
    token = re.sub(r"\s+", " ", m.group(1).upper())
    token = re.sub(r"^(IFRS|IAS|IFRIC|ISQM|ISA|ISRE|ISAE|ISSA|ISRS)(\d)", r"\1 \2", token)
    token = re.sub(r"^IFRS\s*S(\d)", r"IFRS S\1", token)
    token = re.sub(r"^SIC\s*(\d+)", r"SIC-\1", token)
    return token


def extract_pdf_text(pdf_path: Path) -> str:
    # 1. 优先尝试 pypdf / PyPDF2
    for mod_name in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(mod_name)
            reader = mod.PdfReader(str(pdf_path))
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            pass
    # 2. 其次尝试 PyMuPDF (fitz)
    try:
        import fitz  # type: ignore
        with fitz.open(str(pdf_path)) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        pass
    # 3. 兜底调用系统 pdftotext（如 Homebrew poppler）
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
    raise RuntimeError(
        "未检测到 PDF 解析引擎。请先安装 pypdf（pip3 install pypdf）或 Homebrew poppler（brew install poppler）。"
    )


def parse_paragraphs(raw_text: str, code: str) -> list[dict]:
    lines = [re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in raw_text.replace("\r\n", "\n").split("\n")]
    articles: list[dict] = []
    cur_no = ""
    cur_lines: list[str] = []

    def flush() -> None:
        nonlocal cur_no, cur_lines
        if cur_no and cur_lines:
            body = re.sub(r"\n{3,}", "\n\n", "\n".join(cur_lines)).strip()
            if len(body) >= 12:
                articles.append(
                    {
                        "no": f"{code}.{cur_no}",
                        "heading": f"Official Paragraph {cur_no} (Local Private Copy)",
                        "text": body,
                        "seq": len(articles),
                    }
                )
        cur_no = ""
        cur_lines = []

    for ln in lines:
        if not ln:
            continue
        # 过滤常见页眉页脚噪音
        if re.match(r"^(©\s*IFRS\s*Foundation|Page\s+\d+|\d+\s+©|A\d{2,4}\s+©)", ln, re.IGNORECASE):
            continue
        m = PARA_LINE_RE.match(ln)
        if m and len(m.group(2)) >= 8:
            flush()
            cur_no = m.group(1)
            cur_lines = [m.group(2)]
        elif cur_no:
            cur_lines.append(ln)
    flush()

    # 若 PDF 非标准段落号格式，退化为按空行分段保存
    if len(articles) < 3:
        chunks = [re.sub(r"\s+", " ", c).strip() for c in re.split(r"\n{2,}", raw_text) if len(c.strip()) >= 40]
        articles = [
            {
                "no": f"Section {idx + 1}",
                "heading": "Local Private Full Text",
                "text": chunk,
                "seq": idx,
            }
            for idx, chunk in enumerate(chunks[:500])
        ]
    return articles


def main() -> int:
    LOCAL_PDF_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_OUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(LOCAL_PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"未在 {LOCAL_PDF_DIR.relative_to(PROJECT_ROOT)}/ 中发现 PDF 文件。")
        print("请将个人下载的官方英文 PDF（如 IFRS_15.pdf、IAS_36.pdf）放入该目录后重新运行。")
        return 0

    imported = 0
    for pdf in pdfs:
        try:
            raw = extract_pdf_text(pdf)
        except Exception as exc:
            print(f"[ERROR] {pdf.name}: {exc}", file=sys.stderr)
            return 1
        code = normalize_code(pdf.stem) or normalize_code(raw[:600])
        if not code:
            print(f"[SKIP] {pdf.name}: 未能识别标准编号（请将文件名改为如 IFRS_15.pdf）")
            continue
        articles = parse_paragraphs(raw, code)
        slug = re.sub(r"[^a-z0-9]+", "_", code.lower()).strip("_")
        out_path = PRIVATE_OUT_DIR / f"{slug}.json"
        payload = {
            "code": code,
            "source_file": pdf.name,
            "imported_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "paragraph_count": len(articles),
            "articles": articles,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] {pdf.name} -> {code}: parsed {len(articles)} paragraphs -> {out_path.relative_to(PROJECT_ROOT)}")
        imported += 1

    print(f"\n完成：共导入 {imported} 份私用 PDF。运行 `python3 scripts/build_site.py --include-private` 生成本机私用站点 site_private/index.html。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
