#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

from repositories.record_repository import create_record, get_latest_record, get_record_by_id, list_records, update_record

DB_PATH = Path('/home/ubuntu/.openclaw/workspace/trade_review_records.sqlite3')


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    user_id = 'validation-user'
    trade_id = 'trade_validation_sqlite_001'

    record = {
        'tradeId': trade_id,
        'userId': user_id,
        'symbol': 'BTC',
        'pair': 'BTCUSDT',
        'side': 'long',
        'leverage': 3,
        'positionSize': '100U',
        'thesis': '验证 SQLite repository',
        'stopLoss': '62000',
        'plannedHoldingTime': '短线',
        'result': 'open',
        'reviewNote': '',
        'snapshotPrice': 63000,
        'snapshotChange24h': 5.2,
        'snapshotLongShortRatio': 1.03,
        'snapshotOpenInterest': 123456.0,
        'snapshotTopTraderLongShortRatio': 1.01,
        'snapshotTime': '2026-03-11T19:00:00Z',
        'createdAt': '2026-03-11T19:00:00Z',
        'updatedAt': '2026-03-11T19:00:00Z',
    }

    existing = get_record_by_id(trade_id)
    if existing is None:
        create_record(record)

    fetched = get_record_by_id(trade_id)
    assert_true(fetched is not None, '应能按 tradeId 取回记录')
    assert_true(fetched['pair'] == 'BTCUSDT', 'pair 应为 BTCUSDT')

    latest = get_latest_record(user_id)
    assert_true(latest is not None, '应能按 userId 取到最近记录')
    assert_true(latest['userId'] == user_id, '最近记录 userId 应匹配')

    records = list_records(user_id=user_id, filters={'pair': 'BTCUSDT'})
    assert_true(len(records) >= 1, '应能按 userId + pair 列出记录')

    updated = update_record(trade_id, {'result': 'break_even', 'reviewNote': 'SQLite 校验通过'})
    assert_true(updated is not None, '应能更新记录')
    assert_true(updated['result'] == 'break_even', '更新后 result 应为 break_even')
    assert_true(updated['reviewNote'] == 'SQLite 校验通过', '更新后 reviewNote 应匹配')

    assert_true(DB_PATH.exists(), 'SQLite 文件应存在')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM trade_review_records WHERE tradeId = ?', (trade_id,))
    count = cur.fetchone()[0]
    conn.close()
    assert_true(count == 1, 'SQLite 中应存在且仅存在一条校验记录')

    print(json.dumps({
        'ok': True,
        'validatedTradeId': trade_id,
        'userId': user_id,
        'sqlitePath': str(DB_PATH),
        'checks': [
            'create_record',
            'get_record_by_id',
            'get_latest_record',
            'list_records',
            'update_record',
            'sqlite_file_exists',
            'sqlite_row_exists'
        ]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
