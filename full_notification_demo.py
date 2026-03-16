#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any

from repositories.delivery_status_repository import get_delivery_record_by_request_id
from services.delivery_service import send_channel_payload, transition_delivery_status
from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request
from telegram_output_mock import render_telegram_payload


DEFAULT_EVENT = {
    'symbol': 'BTC',
    'pair': 'BTCUSDT',
    'listingTime': '2026-03-11 18:00（UTC+8）',
}

DEFAULT_PLAN = {
    'pair': 'BTCUSDT',
    'side': '做空',
    'leverage': 10,
    'position_size': '未提供',
    'holding': '短线',
    'reason': '涨太多了，想吃一波回调',
}


def maybe_apply_receipt_writeback(delivery_result: Dict[str, Any], receipt_mode: str | None):
    if not receipt_mode:
        return None

    if delivery_result.get('deliveryStatus') != 'sent':
        return {
            'ok': False,
            'error': 'RECEIPT_NOT_APPLICABLE',
            'message': f"deliveryStatus={delivery_result.get('deliveryStatus')} cannot apply receipt writeback",
        }

    request_id = delivery_result.get('requestId')
    record = get_delivery_record_by_request_id(request_id)
    if not record:
        return {
            'ok': False,
            'error': 'DELIVERY_RECORD_NOT_FOUND',
            'message': f'delivery record not found: {request_id}',
        }

    if receipt_mode == 'delivered':
        after = transition_delivery_status(record, 'delivered')
    elif receipt_mode == 'failed':
        after = transition_delivery_status(record, 'failed')
    else:
        raise ValueError(f'unsupported receiptMode: {receipt_mode}')

    return {
        'ok': True,
        'receiptMode': receipt_mode,
        'before': record,
        'after': after,
    }



def run_full_notification_demo(mode: str = 'review', payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    receipt_mode = payload.get('receiptMode')

    if mode == 'review':
        event = payload.get('event') or DEFAULT_EVENT
        job = {
            'jobName': 'listing-alert-review',
            'action': 'alert_to_review',
            'payload': {'event': event},
            'requestId': 'full-demo-review-001',
            'traceId': 'trace-full-demo-review-001',
            'userId': payload.get('userId'),
        }
    elif mode == 'risk':
        event = payload.get('event') or DEFAULT_EVENT
        plan = payload.get('plan') or DEFAULT_PLAN
        job = {
            'jobName': 'listing-alert-risk',
            'action': 'alert_to_risk',
            'payload': {'event': event, 'plan': plan},
            'requestId': 'full-demo-risk-001',
            'traceId': 'trace-full-demo-risk-001',
            'userId': payload.get('userId'),
        }
    else:
        raise ValueError(f'unsupported mode: {mode}')

    runtime_result = handle_scheduler_runtime_request(job)
    notification_output = render_notification_from_runtime_result(runtime_result)
    telegram_payload = render_telegram_payload(notification_output)
    delivery_result = send_channel_payload(telegram_payload)
    receipt_writeback = maybe_apply_receipt_writeback(delivery_result, receipt_mode)

    return {
        'mode': mode,
        'job': job,
        'runtimeResult': runtime_result,
        'notificationOutput': notification_output,
        'telegramPayload': telegram_payload,
        'deliveryResult': delivery_result,
        'receiptWriteback': receipt_writeback,
    }



def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'review'
    payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = run_full_notification_demo(mode, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
