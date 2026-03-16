#!/usr/bin/env python3
import json

from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    success = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-review',
        'action': 'alert_to_review',
        'payload': {
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            }
        },
        'requestId': 'sched-job-001',
        'traceId': 'trace-sched-001',
    })
    assert_true(success['ok'] is True, 'Scheduler mock alert_to_review 应成功')
    assert_true(success['runtimeMeta']['channel'] == 'scheduler', 'channel 应为 scheduler')
    assert_true(success['runtimeMeta']['requestId'] == 'sched-job-001', 'requestId 应透传')
    assert_true(success['runtimeMeta']['traceId'] == 'trace-sched-001', 'traceId 应透传')
    cases.append('scheduler_mock_alert_to_review_success')

    invalid = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-review',
        'action': 'alert_to_review',
        'payload': {
            'event': {
                'symbol': 'BTC'
            }
        }
    })
    assert_true(invalid['ok'] is False, 'Scheduler mock 非法 event 应失败')
    assert_true(invalid['error'] == 'INVALID_INPUT', 'Scheduler mock 非法 event 应返回 INVALID_INPUT')
    assert_true(bool(invalid['runtimeMeta']['requestId']), '未显式传 requestId 时也应自动补 requestId')
    cases.append('scheduler_mock_invalid_input')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
