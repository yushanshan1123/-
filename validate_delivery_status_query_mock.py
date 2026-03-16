#!/usr/bin/env python3
import json

from delivery_status_query_mock import handle_delivery_status_query
from delivery_facade_mock import simulate_channel_delivery


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    simulate_channel_delivery({
        'channel': 'telegram',
        'targetUserId': 'telegram:test-user',
        'message': 'hello',
        'requestId': 'query-test-001',
        'traceId': 'trace-query-test-001',
    })

    latest = handle_delivery_status_query({'kind': 'latest', 'userId': 'telegram:test-user'})
    assert_true(latest['ok'] is True, 'latest 查询应成功')
    assert_true(latest['record'] is not None, 'latest 查询应返回记录')
    assert_true(latest['record']['targetUserId'] == 'telegram:test-user', 'latest 查询 userId 应匹配')
    cases.append('query_latest_delivery_record')

    by_request = handle_delivery_status_query({'kind': 'by_request_id', 'requestId': 'query-test-001'})
    assert_true(by_request['ok'] is True, 'by_request_id 查询应成功')
    assert_true(by_request['record'] is not None, 'by_request_id 查询应返回记录')
    assert_true(by_request['record']['requestId'] == 'query-test-001', 'requestId 应匹配')
    cases.append('query_delivery_record_by_request_id')

    listed = handle_delivery_status_query({'kind': 'list', 'userId': 'telegram:test-user', 'limit': 5})
    assert_true(listed['ok'] is True, 'list 查询应成功')
    assert_true(len(listed['records']) >= 1, 'list 查询应至少返回一条记录')
    cases.append('list_delivery_records')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
