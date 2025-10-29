from __future__ import annotations
import argparse, os, sys, platform, mimetypes, base64, json, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs" / "publication"
DRAFTS = OUTPUTS / "drafts"
LOGS = ROOT / "logs"
DRAFTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _append_jsonl(record: Dict, yyyymm: str):
    log_path = LOGS / f"publication_agent_{yyyymm}.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _load_html(yyyymm: str, locale: str, explicit_path: Optional[str]) -> str:
    if explicit_path:
        return _read_text(Path(explicit_path))
    fname = f"publication_email_{yyyymm}_{'en' if locale=='en' else 'fr'}.html"
    p = OUTPUTS / fname
    if not p.exists():
        raise FileNotFoundError(f"HTML draft not found: {p}")
    return _read_text(p)

def _collect_attachments(paths: List[str]) -> List[Path]:
    files = []
    for p in paths or []:
        pa = (ROOT / p).resolve() if not os.path.isabs(p) else Path(p)
        if not pa.exists():
            raise FileNotFoundError(f"Attachment not found: {pa}")
        files.append(pa)
    return files

# -----------------------
# .EML cross-platform
# -----------------------
def save_eml(subject: str, html_body: str, to: List[str], cc: List[str], attachments: List[Path], save_path: Path):
    # Minimal RFC 5322 MIME with HTML body + attachments (base64)
    boundary = "====MTCR_BOUNDARY===="
    lines = []
    lines.append(f"Subject: {subject}")
    if to: lines.append(f"To: {', '.join(to)}")
    if cc: lines.append(f"Cc: {', '.join(cc)}")
    lines.append("MIME-Version: 1.0")
    lines.append(f'Content-Type: multipart/mixed; boundary="{boundary}"')
    lines.append("")
    lines.append(f"--{boundary}")
    lines.append('Content-Type: text/html; charset="utf-8"')
    lines.append("Content-Transfer-Encoding: 8bit")
    lines.append("")
    lines.append(html_body)
    for att in attachments:
        ctype, _ = mimetypes.guess_type(str(att))
        if ctype is None: ctype = "application/octet-stream"
        lines.append(f"--{boundary}")
        lines.append(f"Content-Type: {ctype}; name=\"{att.name}\"")
        lines.append("Content-Transfer-Encoding: base64")
        lines.append(f"Content-Disposition: attachment; filename=\"{att.name}\"")
        lines.append("")
        with att.open("rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        # wrap at 76 chars per RFC
        lines += [b64[i:i+76] for i in range(0, len(b64), 76)]
    lines.append(f"--{boundary}--")
    save_path.write_text("\r\n".join(lines), encoding="utf-8")

# -----------------------
# .MSG via Outlook (Windows)
# -----------------------
def save_msg(subject: str, html_body: str, to: List[str], cc: List[str], attachments: List[Path], save_path: Path):
    try:
        import win32com.client  # type: ignore
    except Exception as e:
        raise RuntimeError("pywin32 not available; cannot create .msg drafts") from e
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # MailItem
    mail.Subject = subject
    if to: mail.To = "; ".join(to)
    if cc: mail.CC = "; ".join(cc)
    mail.HTMLBody = html_body
    for att in attachments:
        mail.Attachments.Add(str(att))
    # 3 = olMSG Unicode format
    mail.SaveAs(str(save_path), 3)

def create_draft(yyyymm: str, locale: str, subject: str, html_path: Optional[str],
                 to: List[str], cc: List[str], attachments: List[str], reviewer: str,
                 force_eml: bool) -> Path:
    html = _load_html(yyyymm, locale, html_path)
    att_files = _collect_attachments(attachments)
    ts_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    base = f"MTCR_Review_Summary_{yyyymm}_{locale}"
    if platform.system() == "Windows" and not force_eml:
        out = DRAFTS / f"{base}.msg"
        save_msg(subject, html, to, cc, att_files, out)
        fmt = "msg"
    else:
        out = DRAFTS / f"{base}.eml"
        save_eml(subject, html, to, cc, att_files, out)
        fmt = "eml"

    record = {
        "module": "M9.1_OutlookDraftExport",
        "month": yyyymm,
        "locale": locale,
        "subject": subject,
        "draft_path": str(out.relative_to(ROOT)),
        "format": fmt,
        "attachments": [str(a.relative_to(ROOT)) if str(a).startswith(str(ROOT)) else str(a) for a in att_files],
        "reviewer": reviewer,
        "timestamp": ts_iso,
        "sha256": _sha256(html),
        "assistive_mode": True
    }
    _append_jsonl(record, yyyymm)
    return out

def main():
    ap = argparse.ArgumentParser(description="M9.1 — Create Outlook draft (.msg on Windows, .eml elsewhere)")
    ap.add_argument("--month", required=True, help="YYYYMM or YYYY-MM")
    ap.add_argument("--locale", choices=["en","fr"], default="en", help="Email language")
    ap.add_argument("--subject", required=True, help="Subject line")
    ap.add_argument("--html", help="Explicit HTML path; otherwise uses M9 output in /outputs/publication/")
    ap.add_argument("--to", nargs="*", default=[], help="Recipient emails")
    ap.add_argument("--cc", nargs="*", default=[], help="CC emails")
    ap.add_argument("--attach", nargs="*", default=[], help="Attachment paths (relative to repo root or absolute)")
    ap.add_argument("--reviewer", required=True, help="Your name for QA log")
    ap.add_argument("--force-eml", action="store_true", help="Force .eml even on Windows")
    args = ap.parse_args()

    yyyymm = args.month.replace("-", "")
    out = create_draft(
        yyyymm=yyyymm,
        locale=args.locale,
        subject=args.subject,
        html_path=args.html,
        to=args.to,
        cc=args.cc,
        attachments=args.attach,
        reviewer=args.reviewer,
        force_eml=args.force_eml
    )
    print(f"[M9.1] Draft ready -> {out}")

if __name__ == "__main__":
    main()
