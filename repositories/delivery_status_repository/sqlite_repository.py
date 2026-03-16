import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path('/home/ubuntu/.openclaw/workspace/delivery_status_records.sqlite3')
LEGACY_JSON_PATH = Path('/home/ubuntu/.openclaw/workspace/delivery_status_records.json')


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema():
    with get_conn() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS delivery_status_records (
                requestId TEXT PRIMARY KEY,
                traceId TEXT,
                deliveryStatus TEXT,
                deliveryChannel TEXT,
                targetUserId TEXT,
                providerMessageId TEXT,
                mockMessageId TEXT,
                sentAt TEXT,
                payloadJson TEXT
            )
            '''
        )
        existing_columns = {
            row['name'] for row in conn.execute("PRAGMA table_info(delivery_status_records)").fetchall()
        }
        if 'providerMessageId' not in existing_columns:
            conn.execute('ALTER TABLE delivery_status_records ADD COLUMN providerMessageId TEXT')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_delivery_target_sent ON delivery_status_records(targetUserId, sentAt)')


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    record = dict(row)
    payload_json = record.get('payloadJson')
    record['payload'] = json.loads(payload_json) if payload_json else None
    del record['payloadJson']
    record['ok'] = True
    return record


def load_legacy_json_records() -> List[Dict[str, Any]]:
    if not LEGACY_JSON_PATH.exists():
        return []
    return json.loads(LEGACY_JSON_PATH.read_text())


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'requestId': record.get('requestId'),
        'traceId': record.get('traceId'),
        'deliveryStatus': record.get('deliveryStatus'),
        'deliveryChannel': record.get('deliveryChannel'),
        'targetUserId': record.get('targetUserId'),
        'providerMessageId': record.get('providerMessageId'),
        'mockMessageId': record.get('mockMessageId'),
        'sentAt': record.get('sentAt'),
        'payloadJson': json.dumps(record.get('payload'), ensure_ascii=False),
    }


def bootstrap_from_legacy_json_if_needed():
    ensure_schema()
    with get_conn() as conn:
        row = conn.execute('SELECT COUNT(*) AS c FROM delivery_status_records').fetchone()
        if row['c'] > 0:
            return
    records = load_legacy_json_records()
    if not records:
        return
    with get_conn() as conn:
        for record in records:
            payload = normalize_record(record)
            conn.execute(
                'INSERT OR IGNORE INTO delivery_status_records (requestId, traceId, deliveryStatus, deliveryChannel, targetUserId, providerMessageId, mockMessageId, sentAt, payloadJson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    payload['requestId'], payload['traceId'], payload['deliveryStatus'], payload['deliveryChannel'],
                    payload['targetUserId'], payload['providerMessageId'], payload['mockMessageId'], payload['sentAt'], payload['payloadJson']
                )
            )


def load_delivery_records() -> List[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM delivery_status_records ORDER BY sentAt ASC, requestId ASC').fetchall()
    return [row_to_dict(row) for row in rows]


def save_delivery_records(records: List[Dict[str, Any]]):
    ensure_schema()
    with get_conn() as conn:
        conn.execute('DELETE FROM delivery_status_records')
        for record in records:
            payload = normalize_record(record)
            conn.execute(
                'INSERT INTO delivery_status_records (requestId, traceId, deliveryStatus, deliveryChannel, targetUserId, providerMessageId, mockMessageId, sentAt, payloadJson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    payload['requestId'], payload['traceId'], payload['deliveryStatus'], payload['deliveryChannel'],
                    payload['targetUserId'], payload['providerMessageId'], payload['mockMessageId'], payload['sentAt'], payload['payloadJson']
                )
            )


def append_delivery_record(record: Dict[str, Any]) -> Dict[str, Any]:
    bootstrap_from_legacy_json_if_needed()
    payload = normalize_record(record)
    with get_conn() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO delivery_status_records (requestId, traceId, deliveryStatus, deliveryChannel, targetUserId, providerMessageId, mockMessageId, sentAt, payloadJson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                payload['requestId'], payload['traceId'], payload['deliveryStatus'], payload['deliveryChannel'],
                payload['targetUserId'], payload['providerMessageId'], payload['mockMessageId'], payload['sentAt'], payload['payloadJson']
            )
        )
    return record


def update_delivery_record_status(request_id: str, delivery_status: str, provider_message_id: str | None = None) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    with get_conn() as conn:
        existing = conn.execute('SELECT * FROM delivery_status_records WHERE requestId = ?', (request_id,)).fetchone()
        if not existing:
            return None
        current_provider_message_id = existing['providerMessageId']
        conn.execute(
            'UPDATE delivery_status_records SET deliveryStatus = ?, providerMessageId = ? WHERE requestId = ?',
            (delivery_status, provider_message_id if provider_message_id is not None else current_provider_message_id, request_id)
        )
        row = conn.execute('SELECT * FROM delivery_status_records WHERE requestId = ?', (request_id,)).fetchone()
    return row_to_dict(row) if row else None


def get_latest_delivery_record(user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    query = 'SELECT * FROM delivery_status_records'
    params: list[Any] = []
    if user_id:
        query += ' WHERE targetUserId = ?'
        params.append(user_id)
    query += ' ORDER BY sentAt DESC, requestId DESC LIMIT 1'
    with get_conn() as conn:
        row = conn.execute(query, tuple(params)).fetchone()
    return row_to_dict(row) if row else None


def get_delivery_record_by_request_id(request_id: str) -> Optional[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM delivery_status_records WHERE requestId = ?', (request_id,)).fetchone()
    return row_to_dict(row) if row else None


def list_delivery_records(user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    bootstrap_from_legacy_json_if_needed()
    query = 'SELECT * FROM delivery_status_records'
    params: list[Any] = []
    if user_id:
        query += ' WHERE targetUserId = ?'
        params.append(user_id)
    query += ' ORDER BY sentAt ASC, requestId ASC'
    if limit is not None:
        query += f' LIMIT {int(limit)}'
    with get_conn() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [row_to_dict(row) for row in rows]
