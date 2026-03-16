#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any

from services.runtime_adapter_service import adapt_external_call


def handle_scheduler_runtime_request(job: Dict[str, Any]) -> Dict[str, Any]:
    action = job.get('action')
    payload = job.get('payload', {})
    context = {
        'channel': 'scheduler',
        'userId': job.get('userId'),
        'source': job.get('source') or 'runtime_adapter_service.scheduler',
        'requestId': job.get('requestId'),
        'traceId': job.get('traceId'),
        'jobName': job.get('jobName'),
    }
    return adapt_external_call(action, payload=payload, context=context)


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 scheduler_runtime_entry_mock.py <job-json>')

    job = json.loads(sys.argv[1])
    result = handle_scheduler_runtime_request(job)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
