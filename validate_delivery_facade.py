#!/usr/bin/env python3
import json
import os

from delivery_facade import deliver_channel_payload, should_use_real_adapter, should_fallback_to_mock


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    os.environ.pop('XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY', None)
    assert_true(should_use_real_adapter() is False, '默认不应启用 real adapter')

    mock_result = deliver_channel_payload({
        'channel': 'telegram',
        'targetUserId': 'telegram:delivery-facade-test',
        'message': 'hello from delivery facade',
        'requestId': 'delivery-facade-001',
        'traceId': 'trace-delivery-facade-001',
    })
    assert_true(mock_result['ok'] is True, '默认应直接走 mock 成功')
    assert_true(mock_result['deliveryStatus'] == 'mock_sent', '默认应回落到 mock_sent')

    assert_true(should_fallback_to_mock({'ok': False, 'error': 'NOT_CONFIGURED'}) is True, 'NOT_CONFIGURED 应允许 fallback')
    assert_true(should_fallback_to_mock({'ok': False, 'error': 'INVALID_DELIVERY_PAYLOAD'}) is False, 'INVALID_DELIVERY_PAYLOAD 不应 fallback')

    os.environ['XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY'] = '1'
    assert_true(should_use_real_adapter() is True, '开关打开后应启用 real adapter')

    fallback_result = deliver_channel_payload({
        'channel': 'telegram',
        'targetUserId': 'telegram:delivery-facade-test',
        'message': 'hello from delivery facade',
        'requestId': 'delivery-facade-002',
        'traceId': 'trace-delivery-facade-002',
    })
    assert_true(fallback_result['ok'] is True, 'NOT_CONFIGURED 时 facade 应 fallback 到 mock 成功')
    assert_true(fallback_result['deliveryStatus'] == 'mock_sent', 'fallback 后应为 mock_sent')

    os.environ.pop('XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY', None)

    print(json.dumps({'ok': True, 'validatedCases': [
        'delivery_facade_default_mock_path',
        'delivery_facade_fallback_policy',
        'delivery_facade_real_adapter_switch',
    ]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
