from fastapi import HTTPException


def validate_csv_headers(headers: list[str], required: list[str]):
    missing = [r for r in required if r not in headers]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")
    return True
