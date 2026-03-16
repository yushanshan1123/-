#!/usr/bin/env python3
import json
import sys

from repositories.delivery_status_repository import append_delivery_record, get_delivery_record_by_request_id
from services.delivery_service import transition_delivery_status
from delivery_result_schema import build_delivery_result


DEFAULT_REQUEST_ID = 'provider-receipt-demo-001'
DEFAULT_TRACE_ID = 'trace-provider-receipt-demo-001'
DEFAULT_USER_ID = 'telegram:provider-receipt-demo-user'
DEFAULT_PROVIDER_MESSAGE_ID = 'provider-demo-message-001'


def run_provider_delivery_receipt_demo(request_id: str = DEFAULT_REQUEST_ID):
    initial = build_delivery_result(
        ok=True,
        delivery_status='sent',
        delivery_channel='telegram',
        target_user_id=DEFAULT_USER_ID,
        request_id=request_id,
        trace_id=DEFAULT_TRACE_ID,
        payload={
            'channel': 'telegram',
            'targetUserId': DEFAULT_USER_ID,
            'message': 'provider receipt demo message',
            'requestId': request_id,
            'traceId': DEFAULT_TRACE_ID,
        },
        provider_message_id=DEFAULT_PROVIDER_MESSAGE_ID,
        mock_message_id=None,
    )
    append_delivery_record(initial)

    before = get_delivery_record_by_request_id(request_id)
    after = transition_delivery_status(before, 'delivered')

    return {
        'ok': True,
        'requestId': request_id,
        'before': before,
        'after': after,
    }


def main():
    request_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REQUEST_ID
    result = run_provider_delivery_receipt_demo(request_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
