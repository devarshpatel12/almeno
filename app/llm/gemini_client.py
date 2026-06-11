import os
import logging
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


def batch_classify(transactions: List[Dict]) -> List[Dict]:
    """Attempt to call Gemini if API key present, otherwise use heuristic fallback.
    Returns list of dicts with 'txn_id', 'category', 'raw'
    """
    if not settings.GEMINI_API_KEY:
        logger.info("No GEMINI_API_KEY set — using local heuristic for categories")
        return [_heuristic(t) for t in transactions]

    # placeholder for real call — will attempt but fallback on exception
    try:
        # here you would call Gemini 1.5 Flash with batching
        # For this assignment we simulate a minimal request and response.
        logger.info("Calling Gemini for batch classification")
        # simulate by returning heuristic but mark raw as 'simulated remote'
        out = []
        for t in transactions:
            res = _heuristic(t)
            res["raw"] = "simulated_gemini_response"
            out.append(res)
        return out
    except Exception as e:
        logger.exception("Gemini call failed, falling back")
        return [_heuristic(t) for t in transactions]


def _heuristic(t: Dict) -> Dict:
    m = (t.get("merchant") or "").lower()
    category = "Other"
    if any(x in m for x in ("swiggy", "zomato", "food")):
        category = "Food"
    elif any(x in m for x in ("flipkart", "amazon", "shopping")):
        category = "Shopping"
    elif any(x in m for x in ("irctc", "makemytrip", "trip")):
        category = "Travel"
    elif any(x in m for x in ("ola", "uber", "taxi")):
        category = "Transport"
    elif any(x in m for x in ("jio", "recharge")):
        category = "Utilities"
    elif "atm" in m or "cash" in m:
        category = "Cash Withdrawal"
    elif any(x in m for x in ("bookmyshow", "movie", "entertain")):
        category = "Entertainment"
    return {"txn_id": t.get("txn_id"), "category": category, "raw": "heuristic"}
