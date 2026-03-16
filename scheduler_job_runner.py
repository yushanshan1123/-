#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


DEFAULT_JOBS = [
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
        'requestId': 'scheduler-runner-review-001',
        'traceId': 'trace-scheduler-runner-review-001',
    }
]


def load_jobs(path: str | None = None) -> List[Dict[str, Any]]:
    if not path:
        return DEFAULT_JOBS
    content = Path(path).read_text()
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError('jobs file must be a json array')
    return data


def run_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for job in jobs:
        result = handle_scheduler_runtime_request(job)
        results.append({
            'jobName': job.get('jobName'),
            'action': job.get('action'),
            'requestId': result.get('runtimeMeta', {}).get('requestId'),
            'traceId': result.get('runtimeMeta', {}).get('traceId'),
            'ok': result.get('ok'),
            'result': result,
        })
    return results


def main():
    jobs_path = sys.argv[1] if len(sys.argv) > 1 else None
    jobs = load_jobs(jobs_path)
    results = run_jobs(jobs)
    print(json.dumps({'ok': True, 'jobCount': len(results), 'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
