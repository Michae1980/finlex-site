#!/usr/bin/env python3
"""
方案 B：本机私用官方 PDF 全文解析导入工具（严格 git-ignored，绝不上传公开仓库）

支持两类官方 PDF 自动识别与解析：
1. 单标准 PDF（如 IFRS_15.pdf、IAS_36.pdf、IFRS_18.pdf、ISA_315.pdf、ISSA_5000.pdf）；
2. 多标准整卷官方手册 PDF（自动拆分为各单条准则 / Part 并提取官方段落号）：
   - IAASB 2026 Handbook（Volumes 1–5：ISQM 1–2、ISA 200–810、ISA for LCE、ISRE、ISAE、ISSA 5000、ISRS）
   - IESBA 2026 Handbook（Volume 1：Parts 1–3、Part 4A、Part 4B；Volume 2：Part 5 IESSA）

使用步骤：
1. 查看官方免费 2026 Handbook 下载入口与推荐文件名：
       python3 scripts/import_private_intl_pdfs.py --list-handbooks
2. （可选）一键下载官方免费直链 IESBA 2026 Handbook Volume 1 PDF 到本机 git-ignored 的 local_pdfs/：
       python3 scripts/import_private_intl_pdfs.py --download-iesba
   或将你通过个人免费 IFRS.org / IAASB / IESBA 账号下载的官方英文 PDF 放入 local_pdfs/；
3. 运行本脚本解析官方段落号（自动识别单标准或整卷手册拆分）：
       python3 scripts/import_private_intl_pdfs.py
4. 运行私用离线构建命令，生成独立的本机离线站点 site_private/index.html（已加入 .gitignore，不污染公开 site/）：
       python3 scripts/build_site.py --include-private
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_PDF_DIR = PROJECT_ROOT / "local_pdfs"
PRIVATE_OUT_DIR = PROJECT_ROOT / "intl_data" / "private"
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"

HANDBOOK_CATALOG = [
    {
        "name": "IAASB 2026 Handbook (Volumes 1–5)",
        "portal": "https://www.iaasb.org/publications/2026-handbook-international-quality-management-auditing-review-sustainability-and-other-assurance",
        "suggested_files": [
            "2026-IAASB-Handbook-Volume-1.pdf (ISQM 1–2, ISA 200–720)",
            "2026-IAASB-Handbook-Volume-2.pdf (ISA 800–810, ISRE, ISAE, ISRS, Assurance Framework)",
            "2026-IAASB-Handbook-Volume-3.pdf (ISA for LCE)",
            "2026-IAASB-Handbook-Volume-4.pdf (ISSA 5000)",
        ],
        "direct_pdf": None,
    },
    {
        "name": "IESBA 2026 Handbook — Volume 1 (Parts 1–3, 4A, 4B)",
        "portal": "https://www.ethicsboard.org/publications/2026-handbook-international-code-ethics-professional-accountants",
        "suggested_files": ["2026-IESBA-HB-Volume-1.pdf"],
        "direct_pdf": "https://ifacweb.blob.core.windows.net/publicfiles/2026-09/2026-IESBA-HB-Volume-1.pdf",
    },
    {
        "name": "IESBA 2026 Handbook — Volume 2 (Part 5 IESSA)",
        "portal": "https://www.ethicsboard.org/publications/2026-handbook-international-code-ethics-professional-accountants",
        "suggested_files": ["2026-IESBA-HB-Volume-2.pdf"],
        "direct_pdf": None,
    },
]

CODE_RE = re.compile(
    r"\b(IFRS\s*S?\d{1,2}|IAS\s*\d{1,2}|IFRIC\s*\d{1,2}|SIC[-\s]*\d{1,2}|ISQM\s*\d|ISA\s*\d{3}|ISRE\s*\d{4}|ISAE\s*\d{4}|ISSA\s*\d{4}|ISRS\s*\d{4})\b",
    re.IGNORECASE,
)

# 匹配 IFRS / IAS / ISA 官方段落号行首（如 "1 ", "31 ", "35A ", "B34 ", "BC12 ", "A42 ", "C1 ", "M1 "）
PARA_LINE_RE = re.compile(r"^((?:BC|IE|DO|AG|IG|B|C|A|M)?\d{1,3}[A-Z]?)\s+(.+)$")

# 匹配 IESBA 官方段落号行首（如 "R111.1 ", "111.2 A1 ", "R400.12 ", "5100.1 A1 ", "R5400.3 "）
IESBA_PARA_RE = re.compile(r"^(R?\d{3,4}\.\d{1,2}(?:\s+A\d{1,2})?)\s+(.+)$")

# 匹配 IAASB Handbook 整卷中的单条准则标题边界
IAASB_SPLIT_RE = re.compile(
    r"^(?:"
    r"INTERNATIONAL\s+STANDARD\s+ON\s+QUALITY\s+MANAGEMENT\s+(\d)"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+AUDITING\s+(\d{3})(?:\s*\(REVISED(?:\s+\d{4})?\))?"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+REVIEW\s+ENGAGEMENTS\s+(\d{4})(?:\s*\(REVISED\))?"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+ASSURANCE\s+ENGAGEMENTS\s+(\d{4})(?:\s*\(REVISED\))?"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+SUSTAINABILITY\s+ASSURANCE\s+(\d{4})"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+RELATED\s+SERVICES\s+(\d{4})(?:\s*\(REVISED\))?"
    r"|INTERNATIONAL\s+FRAMEWORK\s+FOR\s+ASSURANCE\s+ENGAGEMENTS"
    r"|INTERNATIONAL\s+STANDARD\s+ON\s+AUDITING\s+FOR\s+AUDITS\s+OF\s+FINANCIAL\s+STATEMENTS\s+OF\s+LESS\s+COMPLEX\s+ENTITIES"
    r")\b",
    re.IGNORECASE,
)

# 匹配 IESBA Handbook 整卷中的 Part 标题边界
IESBA_PART_SPLIT_RE = re.compile(
    r"^PART\s+(1|2|3|4A|4B|5)\b(?:\s*[—–\-:]|\s+[A-Z])",
    re.IGNORECASE,
)


def load_canonical_code_map() -> dict[str, str]:
    """从公开 intl_data/*.json 读取标准规范 code（如 ISA 315 -> ISA 315 (Revised 2019)）。"""
    mapping: dict[str, str] = {}
    if not INTL_DATA_DIR.exists():
        return mapping
    for jf in sorted(INTL_DATA_DIR.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        for doc in data.get("documents", []):
            code = (doc.get("code") or "").strip()
            if not code:
                continue
            mapping[code.upper()] = code
            base = re.sub(r"\s*\(revised[^)]*\)", "", code, flags=re.IGNORECASE).strip().upper()
            mapping.setdefault(base, code)
    return mapping


def normalize_code(raw: str, canonical_map: dict[str, str] | None = None) -> str:
    s = re.sub(r"[_-]+", " ", raw).strip()
    if re.search(r"\bISA\s+for\s+LCE\b|LESS\s+COMPLEX\s+ENTITIES", s, re.IGNORECASE):
        return "ISA for LCE"
    m = CODE_RE.search(s)
    if not m:
        return ""
    token = re.sub(r"\s+", " ", m.group(1).upper())
    token = re.sub(r"^(IFRS|IAS|IFRIC|ISQM|ISA|ISRE|ISAE|ISSA|ISRS)(\d)", r"\1 \2", token)
    token = re.sub(r"^IFRS\s*S(\d)", r"IFRS S\1", token)
    token = re.sub(r"^SIC\s*(\d+)", r"SIC-\1", token)
    if canonical_map and token.upper() in canonical_map:
        return canonical_map[token.upper()]
    return token


def extract_pdf_text(pdf_path: Path) -> str:
    for mod_name in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(mod_name)
            reader = mod.PdfReader(str(pdf_path))
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            pass
    try:
        import fitz  # type: ignore
        with fitz.open(str(pdf_path)) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception:
        pass
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


def clean_noise_line(ln: str) -> bool:
    return bool(
        re.match(
            r"^(©\s*(?:IFRS\s*Foundation|IFAC|IAASB|IESBA)|Page\s+\d+|\d+\s+©|A\d{2,4}\s+©|HANDBOOK\s+OF\s+INTERNATIONAL|THE\s+INTERNATIONAL\s+CODE\s+OF\s+ETHICS)",
            ln,
            re.IGNORECASE,
        )
    )


def parse_paragraphs(raw_text: str, code: str, *, is_iesba: bool = False) -> list[dict]:
    lines = [re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in raw_text.replace("\r\n", "\n").split("\n")]
    articles: list[dict] = []
    cur_no = ""
    cur_lines: list[str] = []
    para_re = IESBA_PARA_RE if is_iesba else PARA_LINE_RE

    def flush() -> None:
        nonlocal cur_no, cur_lines
        if cur_no and cur_lines:
            body = re.sub(r"\n{3,}", "\n\n", "\n".join(cur_lines)).strip()
            if len(body) >= 12:
                art_no = cur_no if is_iesba else f"{code}.{cur_no}"
                articles.append(
                    {
                        "no": art_no,
                        "heading": f"Official Paragraph {cur_no} (Local Private Copy)",
                        "text": body,
                        "seq": len(articles),
                    }
                )
        cur_no = ""
        cur_lines = []

    for ln in lines:
        if not ln or clean_noise_line(ln):
            continue
        m = para_re.match(ln)
        if m and len(m.group(2)) >= 8:
            flush()
            cur_no = m.group(1).strip()
            cur_lines = [m.group(2)]
        elif cur_no:
            cur_lines.append(ln)
    flush()

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


def split_iesba_handbook(raw_text: str) -> dict[str, str]:
    """将 IESBA 2026 Handbook PDF 按 Part 1–3 / Part 4A / Part 4B / Part 5 (IESSA) 拆分。"""
    part_to_code = {
        "1": "IESBA Code Part 1–3",
        "2": "IESBA Code Part 1–3",
        "3": "IESBA Code Part 1–3",
        "4A": "IESBA Code Part 4A",
        "4B": "IESBA Code Part 4B",
        "5": "IESBA Code Part 5 (IESSA)",
    }
    buckets: dict[str, list[str]] = {}
    cur_code = ""
    lines = raw_text.replace("\r\n", "\n").split("\n")
    for ln in lines:
        s = re.sub(r"[ \t\u00a0]+", " ", ln).strip()
        m = IESBA_PART_SPLIT_RE.match(s)
        if m:
            # 跳过目录页行（通常以页码数字结尾）
            if not re.search(r"\.{3,}\s*\d+$|\s+\d{1,4}$", s):
                p_key = m.group(1).upper()
                cur_code = part_to_code.get(p_key, "")
                if cur_code:
                    buckets.setdefault(cur_code, []).append(s)
                    continue
        if cur_code:
            buckets.setdefault(cur_code, []).append(ln)
    return {k: "\n".join(v) for k, v in buckets.items() if len("\n".join(v)) >= 800}


def split_iaasb_handbook(raw_text: str, canonical_map: dict[str, str]) -> dict[str, str]:
    """将 IAASB 2026 Handbook 多标准整卷 PDF 按标准标题自动拆分为各单条准则正文。"""
    buckets: dict[str, list[str]] = {}
    cur_code = ""
    lines = raw_text.replace("\r\n", "\n").split("\n")
    for ln in lines:
        s = re.sub(r"[ \t\u00a0]+", " ", ln).strip()
        m = IAASB_SPLIT_RE.match(s)
        is_toc = bool(re.search(r"\.{2,}\s*\d+$", s) or (m and len(s) > m.end() + 4 and re.search(r"\s\d{1,4}$", s[m.end():])))
        if m and not is_toc:
            if m.group(1):
                raw_code = f"ISQM {m.group(1)}"
            elif m.group(2):
                raw_code = f"ISA {m.group(2)}"
            elif m.group(3):
                raw_code = f"ISRE {m.group(3)}"
            elif m.group(4):
                raw_code = f"ISAE {m.group(4)}"
            elif m.group(5):
                raw_code = f"ISSA {m.group(5)}"
            elif m.group(6):
                raw_code = f"ISRS {m.group(6)}"
            elif "LESS COMPLEX ENTITIES" in s.upper():
                raw_code = "ISA for LCE"
            else:
                raw_code = "Assurance Framework"
            cur_code = canonical_map.get(raw_code.upper(), raw_code)
            buckets.setdefault(cur_code, []).append(s)
            continue
        if cur_code:
            buckets.setdefault(cur_code, []).append(ln)
    return {k: "\n".join(v) for k, v in buckets.items() if len("\n".join(v)) >= 800}


def detect_handbook_kind(pdf_name: str, head_text: str) -> str:
    combined = f"{pdf_name} {head_text[:4000]}".upper()
    if "IESBA" in combined or "INTERNATIONAL CODE OF ETHICS FOR PROFESSIONAL ACCOUNTANTS" in combined:
        if "HANDBOOK" in combined or "VOLUME" in combined or "HB" in combined:
            return "iesba_handbook"
    if "IAASB" in combined or "HANDBOOK OF INTERNATIONAL QUALITY MANAGEMENT" in combined:
        if "HANDBOOK" in combined or "VOLUME" in combined:
            return "iaasb_handbook"
    return "single"


def write_private_json(code: str, source_file: str, articles: list[dict]) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "_", code.lower()).strip("_")
    out_path = PRIVATE_OUT_DIR / f"{slug}.json"
    payload = {
        "code": code,
        "source_file": source_file,
        "imported_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "paragraph_count": len(articles),
        "articles": articles,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def print_handbook_catalog() -> None:
    print("官方免费 2026 Handbook 下载入口（仅限个人本机查阅，严禁上传公开仓库）：\n")
    for item in HANDBOOK_CATALOG:
        print(f"- {item['name']}")
        print(f"  官方页面: {item['portal']}")
        if item["direct_pdf"]:
            print(f"  官方直链: {item['direct_pdf']}")
        print(f"  建议放入 local_pdfs/: {', '.join(item['suggested_files'])}\n")


def download_iesba_vol1() -> int:
    LOCAL_PDF_DIR.mkdir(parents=True, exist_ok=True)
    url = HANDBOOK_CATALOG[1]["direct_pdf"]
    dest = LOCAL_PDF_DIR / "2026-IESBA-HB-Volume-1.pdf"
    print(f"正在下载官方免费 IESBA 2026 Handbook Volume 1 -> {dest.relative_to(PROJECT_ROOT)} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (FinLex Personal Study Tool)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        kb = dest.stat().st_size / 1024
        print(f"[OK] 已下载 {dest.name} ({kb:.1f} KB)")
        return 0
    except Exception as exc:
        print(f"[ERROR] 下载失败：{exc}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="本机私用官方 IFRS / IAASB / IESBA PDF 全文解析导入工具")
    parser.add_argument("--list-handbooks", action="store_true", help="列出 IAASB / IESBA 2026 官方免费手册下载入口")
    parser.add_argument("--download-iesba", action="store_true", help="下载官方免费 IESBA 2026 Handbook Vol.1 PDF 到 local_pdfs/")
    parser.add_argument("--mode", choices=("auto", "single", "iaasb", "iesba"), default="auto", help="解析模式（默认自动识别单标准或整卷手册）")
    args = parser.parse_args()

    if args.list_handbooks:
        print_handbook_catalog()
        return 0

    if args.download_iesba:
        rc = download_iesba_vol1()
        if rc != 0:
            return rc

    LOCAL_PDF_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    canonical_map = load_canonical_code_map()

    pdfs = sorted(LOCAL_PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"未在 {LOCAL_PDF_DIR.relative_to(PROJECT_ROOT)}/ 中发现 PDF 文件。")
        print("提示：可运行 `--list-handbooks` 查看官方免费 2026 Handbook 入口，或放入 IFRS_15.pdf / IAASB / IESBA PDF 后重试。")
        return 0

    imported_standards = 0
    for pdf in pdfs:
        try:
            raw = extract_pdf_text(pdf)
        except Exception as exc:
            print(f"[ERROR] {pdf.name}: {exc}", file=sys.stderr)
            return 1

        kind = args.mode
        if kind == "auto":
            kind = detect_handbook_kind(pdf.name, raw)

        if kind in ("iesba", "iesba_handbook"):
            sections = split_iesba_handbook(raw)
            if sections:
                for code, sec_txt in sections.items():
                    arts = parse_paragraphs(sec_txt, code, is_iesba=True)
                    out_path = write_private_json(code, pdf.name, arts)
                    print(f"[OK][IESBA Handbook] {pdf.name} -> {code}: {len(arts)} paragraphs -> {out_path.relative_to(PROJECT_ROOT)}")
                    imported_standards += 1
                continue

        if kind in ("iaasb", "iaasb_handbook"):
            sections = split_iaasb_handbook(raw, canonical_map)
            if len(sections) >= 2 or (len(sections) == 1 and "HANDBOOK" in pdf.name.upper()):
                for code, sec_txt in sections.items():
                    arts = parse_paragraphs(sec_txt, code, is_iesba=False)
                    out_path = write_private_json(code, pdf.name, arts)
                    print(f"[OK][IAASB Handbook] {pdf.name} -> {code}: {len(arts)} paragraphs -> {out_path.relative_to(PROJECT_ROOT)}")
                    imported_standards += 1
                continue

        code = normalize_code(pdf.stem, canonical_map) or normalize_code(raw[:1000], canonical_map)
        if not code:
            print(f"[SKIP] {pdf.name}: 未能识别标准编号（请将文件名改为如 IFRS_15.pdf、ISA_315.pdf 或 2026-IAASB-Handbook-Volume-1.pdf）")
            continue
        is_iesba_single = code.upper().startswith("IESBA")
        articles = parse_paragraphs(raw, code, is_iesba=is_iesba_single)
        out_path = write_private_json(code, pdf.name, articles)
        print(f"[OK] {pdf.name} -> {code}: parsed {len(articles)} paragraphs -> {out_path.relative_to(PROJECT_ROOT)}")
        imported_standards += 1

    print(
        f"\n完成：共解析导入 {imported_standards} 份私用标准/分卷全文。"
        "\n运行 `python3 scripts/build_site.py --include-private` 生成本机私用站点 site_private/index.html。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
