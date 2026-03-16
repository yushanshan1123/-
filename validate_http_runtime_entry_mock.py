#!/usr/bin/env python3
import json

from http_runtime_entry_mock import handle_http_runtime_request


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    success = handle_http_runtime_request(
        body={
            'action': 'risk_check',
            'payload': {
                'pair': 'BTCUSDT',
                'side': '做空',
                'leverage': 10,
                'position_size': '未提供',
                'holding': '短线',
                'reason': '涨太多了，想吃一波回调',
            },
            'userId': 'telegram:6482140148',
        },
        headers={
            'X-Request-Id': 'http-req-001',
            'X-Trace-Id': 'http-trace-001',
        }
    )
    assert_true(success['ok'] is True, 'HTTP mock risk_check 应成功')
    assert_true(success['runtimeMeta']['channel'] == 'http', 'channel 应为 http')
    assert_true(success['runtimeMeta']['requestId'] == 'http-req-001', 'requestId 应从 header 透传')
    assert_true(success['runtimeMeta']['traceId'] == 'http-trace-001', 'traceId 应从 header 透传')
    cases.append('http_mock_risk_check_success')

    invalid = handle_http_runtime_request(
        body={
            'action': 'risk_check',
            'payload': {
                'pair': 'BTCUSDT',
                'side': 'hold'
            },
            'userId': 'telegram:6482140148',
        },
        headers={}
    )
    assert_true(invalid['ok'] is False, 'HTTP mock 非法 side 应失败')
    assert_true(invalid['error'] == 'INVALID_INPUT', 'HTTP mock 非法 side 应返回 INVALID_INPUT')
    assert_true(bool(invalid['runtimeMeta']['requestId']), '未传 header 时也应自动补 requestId')
    cases.append('http_mock_invalid_input')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
