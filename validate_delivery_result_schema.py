#!/usr/bin/env python3
import json

from delivery_result_schema import build_delivery_result


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    result = build_delivery_result(
        ok=True,
        delivery_status='mock_sent',
        delivery_channel='telegram',
        target_user_id='telegram:test-result-schema',
        request_id='delivery-result-schema-001',
        trace_id='trace-delivery-result-schema-001',
        payload={'channel': 'telegram', 'message': 'hello'},
        mock_message_id='mock-001',
    )

    assert_true(result['ok'] is True, 'ok 应为 True')
    assert_true(result['deliveryStatus'] == 'mock_sent', 'deliveryStatus 应正确')
    assert_true(result['deliveryChannel'] == 'telegram', 'deliveryChannel 应正确')
    assert_true(result['providerMessageId'] is None, 'mock 阶段 providerMessageId 应为空')
    assert_true(result['mockMessageId'] == 'mock-001', 'mockMessageId 应正确')
    assert_true(bool(result['sentAt']), 'sentAt 应自动生成')

    print(json.dumps({'ok': True, 'validatedCases': ['build_delivery_result_mock_sent']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
