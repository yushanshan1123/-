#!/usr/bin/env python3
import json

from services.runtime_adapter_service import adapt_external_call, adapt_telegram_runtime_call


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    external = adapt_external_call(
        'risk_check',
        payload={
            'pair': 'BTCUSDT',
            'side': '做空',
            'leverage': 10,
            'position_size': '未提供',
            'holding': '短线',
            'reason': '涨太多了，想吃一波回调',
        },
        context={'channel': 'test', 'userId': 'u-1', 'source': 'adapter-test'}
    )
    assert_true(external['ok'] is True, 'adapt_external_call 应成功调用 runtime')
    assert_true(external['runtimeMeta']['action'] == 'risk_check', 'action 应为 risk_check')
    assert_true(bool(external['runtimeMeta']['requestId']), 'external requestId 应存在')
    assert_true(bool(external['runtimeMeta']['traceId']), 'external traceId 应存在')
    cases.append('adapt_external_call_success')

    telegram = adapt_telegram_runtime_call(
        'alert_to_review',
        payload={
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            }
        },
        user_id='telegram:6482140148',
        request_id='req-test-001',
        trace_id='trace-test-001'
    )
    assert_true(telegram['ok'] is True, 'adapt_telegram_runtime_call 应成功调用 runtime')
    assert_true(telegram['runtimeMeta']['channel'] == 'telegram', 'channel 应为 telegram')
    assert_true(telegram['runtimeMeta']['userId'] == 'telegram:6482140148', 'userId 应透传到 runtimeMeta')
    assert_true(telegram['runtimeMeta']['requestId'] == 'req-test-001', 'requestId 应透传到 runtimeMeta')
    assert_true(telegram['runtimeMeta']['traceId'] == 'trace-test-001', 'traceId 应透传到 runtimeMeta')
    cases.append('adapt_telegram_runtime_call_success')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
