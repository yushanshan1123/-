#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any
from uuid import uuid4

from repositories.delivery_status_repository import append_delivery_record
from delivery_result_schema import build_delivery_result


def simulate_channel_delivery(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get('channel') or 'unknown'
    target = payload.get('targetUserId')
    result = build_delivery_result(
        ok=True,
        delivery_status='mock_sent',
        delivery_channel=channel,
        target_user_id=target,
        request_id=payload.get('requestId'),
        trace_id=payload.get('traceId'),
        payload=payload,
        mock_message_id=f'mock-{channel}-{uuid4().hex[:10]}',
    )
    append_delivery_record(result)
    return result


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 delivery_facade_mock.py <channel-payload-json>')
    payload = json.loads(sys.argv[1])
    result = simulate_channel_delivery(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
