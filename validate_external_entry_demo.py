#!/usr/bin/env python3
import json

from external_entry_demo import (
    run_http_risk_check_demo,
    run_scheduler_review_demo,
    run_notification_review_demo,
)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    http_result = run_http_risk_check_demo()
    assert_true(http_result['ok'] is True, 'http demo 应成功')
    assert_true(http_result['statusCode'] == 200, 'http demo 应返回 200')
    assert_true(http_result['result']['ok'] is True, 'http demo runtime 应成功')

    scheduler_result = run_scheduler_review_demo()
    assert_true(scheduler_result['ok'] is True, 'scheduler demo 应成功')
    assert_true(scheduler_result['result']['jobCount'] == 1, 'scheduler demo 应执行 1 个 job')
    assert_true(scheduler_result['result']['results'][0]['ok'] is True, 'scheduler demo job 应成功')

    notification_result = run_notification_review_demo()
    assert_true(notification_result['ok'] is True, 'notification demo 应成功')
    assert_true(notification_result['result']['deliveryResult']['deliveryStatus'] == 'mock_sent', 'notification demo 应走 mock_sent')

    print(json.dumps({
        'ok': True,
        'validatedCases': [
            'external_entry_demo_http',
            'external_entry_demo_scheduler',
            'external_entry_demo_notification',
        ]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
