import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

RECORDS_PATH = Path('/home/ubuntu/.openclaw/workspace/trade_review_records.json')


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_records() -> List[Dict[str, Any]]:
    if not RECORDS_PATH.exists():
        return []
    return json.loads(RECORDS_PATH.read_text())


def save_records(records: List[Dict[str, Any]]):
    RECORDS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2))


def next_trade_id(records: List[Dict[str, Any]]) -> str:
    return f"trade_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{len(records)+1:03d}"


def create_record(record: Dict[str, Any]) -> Dict[str, Any]:
    records = load_records()
    if not record.get('tradeId'):
        record['tradeId'] = next_trade_id(records)
    records.append(record)
    save_records(records)
    return record


def get_latest_record(user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    records = load_records()
    if user_id:
        records = [r for r in records if r.get('userId') == user_id]
    return records[-1] if records else None


def get_record_by_id(trade_id: str) -> Optional[Dict[str, Any]]:
    records = load_records()
    for record in records:
        if record.get('tradeId') == trade_id:
            return record
    return None


def list_records(user_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    records = load_records()
    if user_id:
        records = [r for r in records if r.get('userId') == user_id]
    filters = filters or {}
    for k, v in filters.items():
        records = [r for r in records if r.get(k) == v]
    return records


def update_record(trade_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    records = load_records()
    for i, record in enumerate(records):
        if record.get('tradeId') == trade_id:
            updated = dict(record)
            updated.update(patch)
            updated['updatedAt'] = utc_now_iso()
            records[i] = updated
            save_records(records)
            return updated
    return None
