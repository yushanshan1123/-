#!/usr/bin/env python3
import json

from provider_delivery_receipt_demo import run_provider_delivery_receipt_demo


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    result = run_provider_delivery_receipt_demo('provider-receipt-demo-validate-001')
    assert_true(result['ok'] is True, 'demo 应成功')
    assert_true(result['before']['deliveryStatus'] == 'sent', 'before 状态应为 sent')
    assert_true(result['after']['deliveryStatus'] == 'delivered', 'after 状态应为 delivered')
    assert_true(result['after']['providerMessageId'] == 'provider-demo-message-001', 'providerMessageId 应保留')

    print(json.dumps({'ok': True, 'validatedCases': ['provider_delivery_receipt_demo_sent_to_delivered']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
