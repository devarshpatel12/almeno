from app.services.csv_processor import clean_row, parse_date, clean_csv_rows, detect_anomalies


def test_parse_date():
    assert parse_date("04-09-2024") is not None
    assert parse_date("2024/02/05") is not None


def test_clean_row_basic():
    r = {"txn_id": "", "date": "04-09-2024", "merchant": "Flipkart", "amount": "$1,000.00", "currency": "inr", "status": "success", "category": "", "account_id": "ACC1", "notes": ""}
    c = clean_row(r)
    assert c["txn_id"]
    assert c["amount"] == 1000.0
    assert c["currency"] == "INR"


def test_dedup_and_anomaly():
    raw = [{"txn_id": "1", "date": "04-09-2024", "merchant": "A", "amount": "10", "currency": "INR", "status": "success", "category": "", "account_id": "ACC1", "notes": ""},
           {"txn_id": "1", "date": "04-09-2024", "merchant": "A", "amount": "10", "currency": "INR", "status": "success", "category": "", "account_id": "ACC1", "notes": ""},
           {"txn_id": "2", "date": "04-09-2024", "merchant": "B", "amount": "1000", "currency": "INR", "status": "success", "category": "", "account_id": "ACC1", "notes": ""}]
    cleaned = clean_csv_rows(raw)
    assert len(cleaned) == 2
    anoms = detect_anomalies(cleaned)
    assert any(a["txn_id"] == cleaned[1]["txn_id"] for a in anoms)
