import json
from pathlib import Path
from typing import Dict, Any, List, Optional

STORE_PATH = Path('/home/ubuntu/.openclaw/workspace/delivery_status_records.json')


def load_delivery_records() -> List[Dict[str, Any]]:
    if not STORE_PATH.exists():
        return []
    return json.loads(STORE_PATH.read_text())


def save_delivery_records(records: List[Dict[str, Any]]):
    STORE_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2))


def append_delivery_record(record: Dict[str, Any]) -> Dict[str, Any]:
    records = load_delivery_records()
    records.append(record)
    save_delivery_records(records)
    return record


def get_latest_delivery_record(user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    records = load_delivery_records()
    if user_id:
        records = [r for r in records if r.get('targetUserId') == user_id]
    return records[-1] if records else None


def get_delivery_record_by_request_id(request_id: str) -> Optional[Dict[str, Any]]:
    for record in reversed(load_delivery_records()):
        if record.get('requestId') == request_id:
            return record
    return None


def list_delivery_records(user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    records = load_delivery_records()
    if user_id:
        records = [r for r in records if r.get('targetUserId') == user_id]
    if limit is not None:
        records = records[-limit:]
    return records
