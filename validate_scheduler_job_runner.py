#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from scheduler_job_runner import run_jobs, load_jobs


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
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
            'requestId': 'sched-runner-001',
            'traceId': 'trace-sched-runner-001',
        },
        {
            'jobName': 'listing-alert-invalid',
            'action': 'alert_to_review',
            'payload': {
                'event': {
                    'symbol': 'BTC'
                }
            },
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / 'jobs.json'
        path.write_text(json.dumps(jobs, ensure_ascii=False))
        loaded = load_jobs(str(path))
        assert_true(len(loaded) == 2, 'jobs 文件应能正确加载')

    results = run_jobs(jobs)
    assert_true(len(results) == 2, '应执行两个 job')
    assert_true(results[0]['ok'] is True, '第一个 job 应成功')
    assert_true(results[0]['requestId'] == 'sched-runner-001', '第一个 job requestId 应透传')
    assert_true(results[1]['ok'] is False, '第二个 job 应失败')
    assert_true(results[1]['result']['error'] == 'INVALID_INPUT', '第二个 job 应返回 INVALID_INPUT')

    print(json.dumps({'ok': True, 'validatedCases': ['scheduler_runner_load_jobs', 'scheduler_runner_execute_jobs']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
