from typing import List, Dict
from app.llm.gemini_client import batch_classify
import logging

logger = logging.getLogger(__name__)


def classify_missing_categories(rows: List[Dict]) -> List[Dict]:
    missing = [r for r in rows if not r.get("category") or r.get("category") == "Uncategorised"]
    if not missing:
        return rows
    # Batch classify
    try:
        results = batch_classify(missing)
    except Exception as e:
        logger.exception("LLM classification failed")
        results = []
    # map back
    for r in rows:
        if r in missing:
            res = next((x for x in results if x["txn_id"] == r["txn_id"]), None)
            if res:
                r["llm_category"] = res["category"]
                r["llm_raw_response"] = res.get("raw")
            else:
                r["llm_failed"] = True
    return rows
