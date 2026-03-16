#!/usr/bin/env python3
import json
import sys

from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


def main():
    if len(sys.argv) > 1:
        event = json.loads(sys.argv[1])
    else:
        event = {
            'symbol': 'BTC',
            'pair': 'BTCUSDT',
            'listingTime': '2026-03-11 18:00（UTC+8）',
        }

    job = {
        'jobName': 'listing-alert-review',
        'action': 'alert_to_review',
        'payload': {
            'event': event,
        },
        'requestId': 'sched-review-demo-001',
        'traceId': 'trace-sched-review-demo-001',
    }
    runtime_result = handle_scheduler_runtime_request(job)
    output = render_notification_from_runtime_result(runtime_result)
    print(json.dumps({
        'runtimeResult': runtime_result,
        'notificationOutput': output,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
