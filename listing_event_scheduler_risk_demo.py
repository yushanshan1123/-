#!/usr/bin/env python3
import json
import sys

from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


def main():
    if len(sys.argv) > 1:
        payload = json.loads(sys.argv[1])
        event = payload['event']
        plan = payload['plan']
    else:
        event = {
            'symbol': 'BTC',
            'pair': 'BTCUSDT',
            'listingTime': '2026-03-11 18:00（UTC+8）',
        }
        plan = {
            'pair': 'BTCUSDT',
            'side': '做空',
            'leverage': 10,
            'position_size': '未提供',
            'holding': '短线',
            'reason': '涨太多了，想吃一波回调',
        }

    job = {
        'jobName': 'listing-alert-risk',
        'action': 'alert_to_risk',
        'payload': {
            'event': event,
            'plan': plan,
        },
        'requestId': 'sched-risk-demo-001',
        'traceId': 'trace-sched-risk-demo-001',
    }
    runtime_result = handle_scheduler_runtime_request(job)
    output = render_notification_from_runtime_result(runtime_result)
    print(json.dumps({
        'runtimeResult': runtime_result,
        'notificationOutput': output,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
