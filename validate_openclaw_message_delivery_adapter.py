#!/usr/bin/env python3
import json

from openclaw_message_delivery_adapter import (
    build_message_send_request,
    execute_message_send_request,
    map_message_send_result,
    send_via_openclaw_message,
)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    request = build_message_send_request({
        'channel': 'telegram',
        'targetUserId': 'telegram:adapter-test-user',
        'message': 'hello adapter',
    })
    assert_true(request['action'] == 'send', '应映射为 send action')
    assert_true(request['target'] == 'telegram:adapter-test-user', 'target 应正确')

    execution = execute_message_send_request(request)
    assert_true(execution['ok'] is False, '执行层当前应返回未实现结果')
    assert_true(execution['error'] == 'NOT_IMPLEMENTED', '执行层当前应返回 NOT_IMPLEMENTED')

    mapped = map_message_send_result(
        {'messageId': 'provider-msg-001'},
        {
            'channel': 'telegram',
            'targetUserId': 'telegram:adapter-test-user',
            'message': 'hello adapter',
            'requestId': 'openclaw-adapter-001',
            'traceId': 'trace-openclaw-adapter-001',
        }
    )
    assert_true(mapped['ok'] is True, 'tool result 映射后应成功')
    assert_true(mapped['deliveryStatus'] == 'sent', '映射后状态应为 sent')
    assert_true(mapped['providerMessageId'] == 'provider-msg-001', 'providerMessageId 应正确映射')

    invalid = send_via_openclaw_message({
        'channel': 'telegram',
        'targetUserId': 'telegram:adapter-test-user',
    })
    assert_true(invalid['ok'] is False, '无 message 时应失败')
    assert_true(invalid['error'] == 'INVALID_DELIVERY_PAYLOAD', '应返回 INVALID_DELIVERY_PAYLOAD')

    not_implemented = send_via_openclaw_message({
        'channel': 'telegram',
        'targetUserId': 'telegram:adapter-test-user',
        'message': 'hello adapter',
        'requestId': 'openclaw-adapter-001',
        'traceId': 'trace-openclaw-adapter-001',
    })
    assert_true(not_implemented['ok'] is False, '未实现执行层当前应返回失败占位结果')
    assert_true(not_implemented['deliveryStatus'] == 'failed', '未实现执行层当前应返回 failed')
    assert_true(not_implemented['error'] == 'NOT_IMPLEMENTED', '应返回 NOT_IMPLEMENTED')

    print(json.dumps({'ok': True, 'validatedCases': [
        'build_message_send_request',
        'execute_message_send_request_not_implemented',
        'map_message_send_result',
        'openclaw_message_delivery_adapter_invalid_payload',
        'openclaw_message_delivery_adapter_not_implemented',
    ]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
