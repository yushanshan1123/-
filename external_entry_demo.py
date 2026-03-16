#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def run_http_risk_check_demo():
    proc = subprocess.Popen(['python3', 'http_runtime_server.py'])
    try:
        time.sleep(1.0)
        payload = {
            'action': 'risk_check',
            'payload': {
                'pair': 'BTCUSDT',
                'side': '做空',
                'leverage': 10,
                'position_size': '未提供',
                'holding': '短线',
                'reason': '涨太多了，想吃一波回调',
            },
            'userId': 'telegram:6482140148',
        }
        req = Request(
            'http://127.0.0.1:8787/runtime',
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'X-Request-Id': 'external-demo-http-001',
                'X-Trace-Id': 'trace-external-demo-http-001',
            },
            method='POST',
        )
        with urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode('utf-8'))
            return {'ok': True, 'transport': 'http', 'statusCode': resp.status, 'result': body}
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def run_scheduler_review_demo():
    jobs = [
        {
            'jobName': 'listing-alert-review',
            'action': 'alert_to_review',
            'payload': {
                'event': {
                    'symbol': 'BTC',
                    'pair': 'BTCUSDT',
                    'listingTime': '2026-03-11 18:00（UTC+8）'
                }
            },
            'requestId': 'external-demo-scheduler-001',
            'traceId': 'trace-external-demo-scheduler-001',
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        jobs_path = Path(tmpdir) / 'jobs.json'
        jobs_path.write_text(json.dumps(jobs, ensure_ascii=False))
        output = subprocess.check_output(['python3', 'scheduler_job_runner.py', str(jobs_path)])
        return {'ok': True, 'transport': 'scheduler', 'result': json.loads(output.decode('utf-8'))}


def run_notification_review_demo():
    output = subprocess.check_output(['python3', 'full_notification_demo.py', 'review'])
    return {'ok': True, 'transport': 'notification', 'result': json.loads(output.decode('utf-8'))}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'http-risk-check':
        result = run_http_risk_check_demo()
    elif mode == 'scheduler-review':
        result = run_scheduler_review_demo()
    elif mode == 'notification-review':
        result = run_notification_review_demo()
    elif mode == 'all':
        result = {
            'ok': True,
            'results': {
                'http-risk-check': run_http_risk_check_demo(),
                'scheduler-review': run_scheduler_review_demo(),
                'notification-review': run_notification_review_demo(),
            }
        }
    else:
        raise SystemExit('usage: python3 external_entry_demo.py [http-risk-check|scheduler-review|notification-review|all]')

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
