#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any

from services.runtime_adapter_service import adapt_external_call


def handle_http_runtime_request(body: Dict[str, Any], headers: Dict[str, Any] | None = None) -> Dict[str, Any]:
    headers = headers or {}
    action = body.get('action')
    payload = body.get('payload', {})
    context = {
        'channel': 'http',
        'userId': body.get('userId'),
        'source': 'runtime_adapter_service.http',
        'requestId': headers.get('X-Request-Id') or headers.get('x-request-id'),
        'traceId': headers.get('X-Trace-Id') or headers.get('x-trace-id'),
    }
    return adapt_external_call(action, payload=payload, context=context)


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 http_runtime_entry_mock.py <body-json> [headers-json]')

    body = json.loads(sys.argv[1])
    headers = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = handle_http_runtime_request(body, headers)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
