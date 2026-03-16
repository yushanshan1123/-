#!/usr/bin/env python3
import json

from full_notification_demo import run_full_notification_demo


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    review = run_full_notification_demo('review')
    assert_true(review['deliveryResult']['deliveryStatus'] == 'mock_sent', '默认 review 应为 mock_sent')
    assert_true(review['receiptWriteback'] is None, '默认不应做 receipt writeback')

    delivered = run_full_notification_demo('review', {'receiptMode': 'delivered'})
    assert_true(delivered['receiptWriteback']['ok'] is False, 'mock_sent 不应直接应用 receipt writeback')
    assert_true(delivered['receiptWriteback']['error'] == 'RECEIPT_NOT_APPLICABLE', 'mock_sent 时应返回 RECEIPT_NOT_APPLICABLE')

    print(json.dumps({'ok': True, 'validatedCases': [
        'full_notification_demo_review',
        'full_notification_demo_receipt_not_applicable_on_mock_sent',
    ]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
