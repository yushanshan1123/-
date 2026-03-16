import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path('/home/ubuntu/.openclaw/workspace/trade_review_records.sqlite3')
LEGACY_JSON_PATH = Path('/home/ubuntu/.openclaw/workspace/trade_review_records.json')


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema():
    with get_conn() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS trade_review_records (
                tradeId TEXT PRIMARY KEY,
                userId TEXT,
                symbol TEXT,
                pair TEXT,
                side TEXT,
                leverage REAL,
                positionSize TEXT,
                thesis TEXT,
                stopLoss TEXT,
                plannedHoldingTime TEXT,
                result TEXT,
                reviewNote TEXT,
                snapshotPrice REAL,
                snapshotChange24h REAL,
                snapshotLongShortRatio REAL,
                snapshotOpenInterest REAL,
                snapshotTopTraderLongShortRatio REAL,
                snapshotTime TEXT,
                createdAt TEXT,
                updatedAt TEXT
            )
            '''
        )
        conn.execute('CREATE INDEX IF NOT EXISTS idx_trade_records_user_created ON trade_review_records(userId, createdAt)')


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)


def next_trade_id() -> str:
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    prefix = f'trade_{today}_'
    with get_conn() as conn:
        row = conn.execute(
            'SELECT tradeId FROM trade_review_records WHERE tradeId LIKE ? ORDER BY tradeId DESC LIMIT 1',
            (f'{prefix}%',),
        ).fetchone()
    if not row:
        return f'{prefix}001'
    last_id = row['tradeId']
    try:
        seq = int(last_id.split('_')[-1]) + 1
    except Exception:
        seq = 1
    return f'{prefix}{seq:03d}'


def load_legacy_json_records() -> List[Dict[str, Any]]:
    if not LEGACY_JSON_PATH.exists():
        return []
    return json.loads(LEGACY_JSON_PATH.read_text())


def bootstrap_from_legacy_json_if_needed():
    ensure_schema()
    with get_conn() as conn:
        row = conn.execute('SELECT COUNT(*) AS c FROM trade_review_records').fetchone()
        if row['c'] > 0:
            return
    legacy_records = load_legacy_json_records()
    if not legacy_records:
        return
    with get_conn() as conn:
        for record in legacy_records:
            payload = normalize_record(record)
            columns = ', '.join(payload.keys())
            placeholders = ', '.join(['?'] * len(payload))
            conn.execute(
                f'INSERT OR IGNORE INTO trade_review_records ({columns}) VALUES ({placeholders})',
                tuple(payload.values()),
            )


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    if not normalized.get('tradeId'):
        normalized['tradeId'] = next_trade_id()
    normalized.setdefault('createdAt', utc_now_iso())
    normalized.setdefault('updatedAt', normalized['createdAt'])
    return normalized


def load_records() -> List[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM trade_review_records ORDER BY createdAt ASC, tradeId ASC').fetchall()
    return [row_to_dict(row) for row in rows]


def save_records(records: List[Dict[str, Any]]):
    ensure_schema()
    with get_conn() as conn:
        conn.execute('DELETE FROM trade_review_records')
        for record in records:
            payload = normalize_record(record)
            columns = ', '.join(payload.keys())
            placeholders = ', '.join(['?'] * len(payload))
            conn.execute(
                f'INSERT INTO trade_review_records ({columns}) VALUES ({placeholders})',
                tuple(payload.values()),
            )


def create_record(record: Dict[str, Any]) -> Dict[str, Any]:
    bootstrap_from_legacy_json_if_needed()
    payload = normalize_record(record)
    with get_conn() as conn:
        columns = ', '.join(payload.keys())
        placeholders = ', '.join(['?'] * len(payload))
        conn.execute(
            f'INSERT INTO trade_review_records ({columns}) VALUES ({placeholders})',
            tuple(payload.values()),
        )
    return payload


def get_latest_record(user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    query = 'SELECT * FROM trade_review_records'
    params: list[Any] = []
    if user_id:
        query += ' WHERE userId = ?'
        params.append(user_id)
    query += ' ORDER BY createdAt DESC, tradeId DESC LIMIT 1'
    with get_conn() as conn:
        row = conn.execute(query, tuple(params)).fetchone()
    return row_to_dict(row) if row else None


def get_record_by_id(trade_id: str) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM trade_review_records WHERE tradeId = ?', (trade_id,)).fetchone()
    return row_to_dict(row) if row else None


def list_records(user_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    query = 'SELECT * FROM trade_review_records'
    clauses = []
    params: list[Any] = []
    if user_id:
        clauses.append('userId = ?')
        params.append(user_id)
    filters = filters or {}
    for k, v in filters.items():
        clauses.append(f'{k} = ?')
        params.append(v)
    if clauses:
        query += ' WHERE ' + ' AND '.join(clauses)
    query += ' ORDER BY createdAt ASC, tradeId ASC'
    with get_conn() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [row_to_dict(row) for row in rows]


def update_record(trade_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    existing = get_record_by_id(trade_id)
    if not existing:
        return None
    updated = dict(existing)
    updated.update(patch)
    updated['updatedAt'] = utc_now_iso()
    with get_conn() as conn:
        assignments = ', '.join([f'{k} = ?' for k in updated.keys() if k != 'tradeId'])
        params = [updated[k] for k in updated.keys() if k != 'tradeId'] + [trade_id]
        conn.execute(f'UPDATE trade_review_records SET {assignments} WHERE tradeId = ?', params)
    return updated
