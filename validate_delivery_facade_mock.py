#!/usr/bin/env python3
import json

from delivery_facade_mock import simulate_channel_delivery
from delivery_status_store_mock import load_delivery_records
from telegram_output_mock import render_telegram_payload
from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    runtime_result = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-review',
        'action': 'alert_to_review',
        'payload': {
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            }
        },
        'userId': 'telegram:6482140148',
        'requestId': 'delivery-test-001',
        'traceId': 'trace-delivery-test-001',
    })
    notification_output = render_notification_from_runtime_result(runtime_result)
    telegram_payload = render_telegram_payload(notification_output)
    delivery_result = simulate_channel_delivery(telegram_payload)

    assert_true(delivery_result['ok'] is True, 'delivery facade mock 应成功')
    assert_true(delivery_result['deliveryStatus'] == 'mock_sent', 'deliveryStatus 应为 mock_sent')
    assert_true(delivery_result['deliveryChannel'] == 'telegram', 'deliveryChannel 应为 telegram')
    assert_true(bool(delivery_result['mockMessageId']), '应生成 mockMessageId')
    cases.append('simulate_telegram_delivery_success')

    records = load_delivery_records()
    assert_true(len(records) >= 1, 'delivery 状态记录应至少有一条')
    assert_true(records[-1]['requestId'] == 'delivery-test-001', '最新 delivery 记录应保留 requestId')
    cases.append('delivery_status_record_saved')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
