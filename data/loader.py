from __future__ import annotations
import json
from typing import Dict, Any,Optional,List

def load_from_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_from_mongo(
    mongo_uri: Optional[str],
    db_name: Optional[str],
    collection_name: Optional[str],
    product_ids: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    if not mongo_uri or not db_name or not collection_name:
        return None
    try:
        from pymongo import MongoClient
    except Exception:
        return None
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        db = client[db_name]
        col = db[collection_name]
        crit_doc = col.find_one({"_type": "criteria"})
        alts = list(col.find({"_type": "alternative"}))
        if product_ids:
            alts = [a for a in alts if a.get("id") in product_ids]
        if not crit_doc or not alts:
            return None
        data = {
            "criteria": crit_doc["criteria"],
            "weights": crit_doc["weights"],
            "alternatives": [
                {"id": a["id"], "name": a["name"], "image": a.get("image"), "values": a["values"]}
                for a in alts
            ]
        }
        return data
    except Exception:
        return None