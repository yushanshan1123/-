#!/usr/bin/env python3
import json

from services.delivery_service import send_channel_payload


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    result = send_channel_payload({
        'channel': 'telegram',
        'targetUserId': 'telegram:test-delivery-service',
        'message': 'hello',
        'requestId': 'delivery-service-001',
        'traceId': 'trace-delivery-service-001',
    })
    assert_true(result['ok'] is True, 'delivery service 应成功返回')
    assert_true(result['deliveryStatus'] == 'mock_sent', '当前 delivery service 应走 mock_sent')
    assert_true(result['deliveryChannel'] == 'telegram', 'deliveryChannel 应正确')
    print(json.dumps({'ok': True, 'validatedCases': ['delivery_service_mock_path']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
