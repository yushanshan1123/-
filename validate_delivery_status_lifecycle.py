#!/usr/bin/env python3
import json

from repositories.delivery_status_repository import get_delivery_record_by_request_id
from services.delivery_service import queue_delivery_record, can_transition_delivery_status, transition_delivery_status


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    request_id = 'delivery-lifecycle-001'
    queued = queue_delivery_record({
        'channel': 'telegram',
        'targetUserId': 'telegram:lifecycle-test-user',
        'requestId': request_id,
        'traceId': 'trace-delivery-lifecycle-001',
        'message': 'queued message',
    })
    assert_true(queued['deliveryStatus'] == 'queued', 'queue_delivery_record 应返回 queued')

    record = get_delivery_record_by_request_id(request_id)
    assert_true(record is not None, 'queued record 应存在')
    assert_true(can_transition_delivery_status('queued', 'sent') is True, 'queued -> sent 应允许')
    assert_true(can_transition_delivery_status('queued', 'delivered') is False, 'queued -> delivered 不应直接允许')

    sent = transition_delivery_status(record, 'sent', provider_message_id='provider-lifecycle-001')
    assert_true(sent['deliveryStatus'] == 'sent', '状态应更新为 sent')
    assert_true(sent['providerMessageId'] == 'provider-lifecycle-001', 'providerMessageId 应写入')

    delivered = transition_delivery_status(sent, 'delivered')
    assert_true(delivered['deliveryStatus'] == 'delivered', '状态应更新为 delivered')
    assert_true(delivered['providerMessageId'] == 'provider-lifecycle-001', 'providerMessageId 应保留')

    print(json.dumps({
        'ok': True,
        'validatedCases': [
            'queue_delivery_record',
            'can_transition_delivery_status',
            'transition_queued_to_sent',
            'transition_sent_to_delivered',
        ]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
