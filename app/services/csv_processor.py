import csv
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4
from statistics import median

SUPPORTED_DATE_FORMATS = ["%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%d"]


def parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    for fmt in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    # try ISO
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def clean_row(row: Dict[str, str]) -> Dict[str, Any]:
    out = {}
    out["txn_id"] = row.get("txn_id") or str(uuid4())
    out["date"] = parse_date(row.get("date", ""))
    out["merchant"] = (row.get("merchant") or "").strip()
    amt = (row.get("amount") or "").replace("$", "").replace(",", "").strip()
    try:
        out["amount"] = float(amt) if amt else 0.0
    except Exception:
        out["amount"] = 0.0
    curr = (row.get("currency") or "").upper().strip()
    out["currency"] = curr if curr else "INR"
    out["status"] = (row.get("status") or "").upper().strip() or "PENDING"
    out["category"] = (row.get("category") or "").strip() or "Uncategorised"
    out["account_id"] = (row.get("account_id") or "").strip()
    out["notes"] = (row.get("notes") or "").strip()
    return out


def read_csv(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def clean_csv_rows(raw_rows: List[Dict[str, str]]):
    cleaned = [clean_row(r) for r in raw_rows]
    # deduplicate by txn signature
    seen = set()
    unique = []
    for r in cleaned:
        sig = (r.get("txn_id"), r.get("amount"), r.get("date"), r.get("merchant"))
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(r)
    return unique


def detect_anomalies(rows: List[Dict[str, Any]]):
    anomalies = []
    # group amounts per account
    by_account = {}
    for r in rows:
        by_account.setdefault(r.get("account_id"), []).append(r.get("amount", 0.0))
    # for each transaction, compute median of other transactions for its account
    for r in rows:
        reasons = []
        acct = r.get("account_id")
        amounts = by_account.get(acct, [])
        # median excluding this transaction's amount
        other_amounts = [a for a in amounts if a != r.get("amount", 0.0)]
        med = median(other_amounts) if other_amounts else 0.0
        if med and r.get("amount", 0) > 3 * med:
            reasons.append("amount_gt_3x_median_excluding_self")
        if r.get("currency") == "USD" and r.get("merchant") in ("Swiggy", "Ola", "IRCTC"):
            reasons.append("usd_merchant_mismatch")
        if reasons:
            anomalies.append({"txn_id": r.get("txn_id"), "reasons": reasons})
    return anomalies
