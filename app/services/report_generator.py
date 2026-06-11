import csv
import json
import zipfile
from pathlib import Path
from typing import Any

from fpdf import FPDF

REPORT_FIELDS = [
    "id",
    "txn_id",
    "date",
    "merchant",
    "amount",
    "currency",
    "status",
    "category",
    "account_id",
    "notes",
    "is_anomaly",
    "anomaly_reason",
    "llm_category",
    "llm_raw_response",
    "llm_failed",
]


def build_report(job_id: str, summary: dict[str, Any], transactions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "summary": summary,
        "transactions": transactions,
    }


def write_json_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)


def write_csv_report(path: Path, transactions: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in transactions:
            writer.writerow({key: row.get(key) for key in REPORT_FIELDS})


def write_pdf_report(path: Path, job_id: str, summary: dict[str, Any], transactions: list[dict[str, Any]], max_rows: int = 30) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Job Report: {job_id}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Summary", ln=True)
    pdf.set_font("Arial", size=11)
    for key, value in summary.items():
        pdf.multi_cell(0, 7, f"{key}: {value}")
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, f"Transactions (first {min(max_rows, len(transactions))})", ln=True)
    pdf.set_font("Arial", size=10)
    for line_index, txn in enumerate(transactions[:max_rows], start=1):
        pdf.multi_cell(
            0,
            6,
            f"{line_index}. {txn.get('date')} | {txn.get('merchant')} | {txn.get('amount')} {txn.get('currency')} | {txn.get('category')} | anomaly={txn.get('is_anomaly')}",
        )
        if pdf.get_y() > 260:
            pdf.add_page()
    pdf.output(path)


def write_zip_report(path: Path, file_paths: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            if file_path.exists():
                zf.write(file_path, arcname=file_path.name)


def generate_reports(job_id: str, summary: dict[str, Any], transactions: list[dict[str, Any]], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"report_{job_id}.json"
    csv_path = output_dir / f"report_{job_id}.csv"
    pdf_path = output_dir / f"report_{job_id}.pdf"
    zip_path = output_dir / f"report_{job_id}.zip"

    report = build_report(job_id, summary, transactions)
    write_json_report(json_path, report)
    write_csv_report(csv_path, transactions)
    write_pdf_report(pdf_path, job_id, summary, transactions)
    write_zip_report(zip_path, [json_path, csv_path, pdf_path])

    return {
        "json": json_path,
        "csv": csv_path,
        "pdf": pdf_path,
        "zip": zip_path,
    }


def ensure_report_format(job_id: str, summary: dict[str, Any], transactions: list[dict[str, Any]], output_dir: Path, fmt: str) -> Path:
    paths = generate_reports(job_id, summary, transactions, output_dir)
    return paths[fmt]
