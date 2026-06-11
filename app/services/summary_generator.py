from typing import List, Dict
from collections import Counter


def generate_summary(rows: List[Dict]) -> Dict:
    total = {}
    merchants = Counter()
    anomalies = 0
    for r in rows:
        cur = r.get("currency") or "INR"
        total[cur] = total.get(cur, 0) + (r.get("amount") or 0)
        if r.get("merchant"):
            merchants[r.get("merchant")] += 1
        if r.get("anomaly_reason"):
            anomalies += 1
    top = [m for m, _ in merchants.most_common(3)]
    if anomalies >= 5:
        risk = "HIGH"
    elif anomalies >= 2:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    narrative = f"Processed {len(rows)} transactions. Top merchants: {', '.join(top)}. Detected {anomalies} anomalies."
    return {
        "total_spend_by_currency": total,
        "top_3_merchants": top,
        "anomaly_count": anomalies,
        "narrative": narrative,
        "risk_level": risk,
    }
