#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any

from repositories.delivery_status_repository import (
    get_latest_delivery_record,
    get_delivery_record_by_request_id,
    list_delivery_records,
)


def handle_delivery_status_query(query: Dict[str, Any]) -> Dict[str, Any]:
    kind = query.get('kind', 'latest')
    user_id = query.get('userId')
    request_id = query.get('requestId')
    limit = query.get('limit')

    if kind == 'latest':
        record = get_latest_delivery_record(user_id)
        return {'ok': True, 'kind': kind, 'record': record}

    if kind == 'by_request_id':
        record = get_delivery_record_by_request_id(request_id)
        return {'ok': True, 'kind': kind, 'record': record}

    if kind == 'list':
        records = list_delivery_records(user_id=user_id, limit=limit)
        return {'ok': True, 'kind': kind, 'records': records}

    return {'ok': False, 'error': 'UNSUPPORTED_QUERY_KIND', 'kind': kind}


def main():
    query = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {'kind': 'latest'}
    result = handle_delivery_status_query(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
