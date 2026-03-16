#!/usr/bin/env python3
import json
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def post_json(url, payload, headers=None):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = Request(url, data=data, headers={**(headers or {}), 'Content-Type': 'application/json'}, method='POST')
    with urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))


def post_json_expect_http_error(url, payload, headers=None):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = Request(url, data=data, headers={**(headers or {}), 'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))


def main():
    proc = subprocess.Popen(['python3', 'http_runtime_server.py'])
    try:
        time.sleep(1.0)
        status, success = post_json(
            'http://127.0.0.1:8787/runtime',
            {
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
            {
                'X-Request-Id': 'http-server-req-001',
                'X-Trace-Id': 'http-server-trace-001',
            }
        )
        assert_true(status == 200, 'HTTP server 成功请求应返回 200')
        assert_true(success['ok'] is True, 'HTTP server risk_check 应成功')
        assert_true(success['runtimeMeta']['requestId'] == 'http-server-req-001', 'requestId 应透传')

        status2, invalid = post_json_expect_http_error(
            'http://127.0.0.1:8787/runtime',
            {
                'action': 'risk_check',
                'payload': {'pair': 'BTCUSDT', 'side': 'hold'},
                'userId': 'telegram:6482140148',
            }
        )
        assert_true(status2 == 400, '非法请求应返回 400')
        assert_true(invalid['ok'] is False, '非法请求应失败')
        assert_true(invalid['error'] == 'INVALID_INPUT', '非法 side 应返回 INVALID_INPUT')

        print(json.dumps({'ok': True, 'validatedCases': ['http_server_risk_check_success', 'http_server_invalid_input']}, ensure_ascii=False, indent=2))
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == '__main__':
    main()
