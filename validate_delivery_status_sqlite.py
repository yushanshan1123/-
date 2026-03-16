#!/usr/bin/env python3
import json
import os
import sqlite3

from repositories.delivery_status_repository import (
    append_delivery_record,
    get_latest_delivery_record,
    get_delivery_record_by_request_id,
    list_delivery_records,
)

DB_PATH = '/home/ubuntu/.openclaw/workspace/delivery_status_records.sqlite3'


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    request_id = 'delivery-sqlite-test-001'
    user_id = 'telegram:sqlite-test-user'
    provider_message_id = 'provider-message-001'

    append_delivery_record({
        'ok': True,
        'deliveryStatus': 'sent',
        'deliveryChannel': 'telegram',
        'targetUserId': user_id,
        'providerMessageId': provider_message_id,
        'mockMessageId': None,
        'sentAt': '2026-03-12T08:55:00Z',
        'requestId': request_id,
        'traceId': 'trace-delivery-sqlite-test-001',
        'payload': {
            'channel': 'telegram',
            'targetUserId': user_id,
            'message': 'sqlite validation message',
            'requestId': request_id,
            'traceId': 'trace-delivery-sqlite-test-001',
        },
    })

    latest = get_latest_delivery_record(user_id)
    assert_true(latest is not None, 'latest 应返回记录')
    assert_true(latest['targetUserId'] == user_id, 'latest userId 应匹配')
    assert_true(latest['providerMessageId'] == provider_message_id, 'latest providerMessageId 应匹配')

    by_request = get_delivery_record_by_request_id(request_id)
    assert_true(by_request is not None, 'by_request_id 应返回记录')
    assert_true(by_request['requestId'] == request_id, 'requestId 应匹配')
    assert_true(by_request['providerMessageId'] == provider_message_id, 'providerMessageId 应匹配')

    listed = list_delivery_records(user_id=user_id, limit=5)
    assert_true(len(listed) >= 1, 'list 应至少返回一条记录')

    assert_true(os.path.exists(DB_PATH), 'SQLite 文件应存在')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT providerMessageId FROM delivery_status_records WHERE requestId = ?', (request_id,))
    row = cur.fetchone()
    conn.close()
    assert_true(row is not None, 'SQLite 表中应存在对应 requestId 记录')
    assert_true(row[0] == provider_message_id, 'SQLite 中 providerMessageId 应正确落地')

    print(json.dumps({
        'ok': True,
        'validatedCases': [
            'append_delivery_record',
            'get_latest_delivery_record',
            'get_delivery_record_by_request_id',
            'list_delivery_records',
            'sqlite_file_exists',
            'sqlite_provider_message_id_exists',
        ]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
