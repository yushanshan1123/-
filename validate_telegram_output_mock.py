#!/usr/bin/env python3
import json

from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request
from telegram_output_mock import render_telegram_payload


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    review_runtime = handle_scheduler_runtime_request({
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
        'requestId': 'sched-review-tg-001',
        'traceId': 'trace-review-tg-001',
    })
    review_output = render_notification_from_runtime_result(review_runtime)
    review_payload = render_telegram_payload(review_output)
    assert_true(review_payload['channel'] == 'telegram', 'Telegram payload channel 应正确')
    assert_true('【新币速评推送】' in review_payload['message'], '速评 Telegram payload 应包含标题')
    assert_true(len(review_payload['buttons']) == 1, '速评 Telegram payload 应带按钮')
    cases.append('render_review_telegram_payload')

    risk_runtime = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-risk',
        'action': 'alert_to_risk',
        'payload': {
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            },
            'plan': {
                'pair': 'BTCUSDT',
                'side': '做空',
                'leverage': 10,
                'position_size': '未提供',
                'holding': '短线',
                'reason': '涨太多了，想吃一波回调'
            }
        },
        'userId': 'telegram:6482140148',
        'requestId': 'sched-risk-tg-001',
        'traceId': 'trace-risk-tg-001',
    })
    risk_output = render_notification_from_runtime_result(risk_runtime)
    risk_payload = render_telegram_payload(risk_output)
    assert_true('【新币风控推送】' in risk_payload['message'], '风控 Telegram payload 应包含标题')
    assert_true(len(risk_payload['buttons']) == 1, '风控 Telegram payload 应带按钮')
    cases.append('render_risk_telegram_payload')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
