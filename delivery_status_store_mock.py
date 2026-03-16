#!/usr/bin/env python3
import json
import sys

from repositories.delivery_status_repository import (
    append_delivery_record,
    get_latest_delivery_record,
    get_delivery_record_by_request_id,
    list_delivery_records,
)


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 delivery_status_store_mock.py <command> [arg]')

    command = sys.argv[1]
    if command == 'append':
        if len(sys.argv) < 3:
            raise SystemExit('usage: python3 delivery_status_store_mock.py append <delivery-result-json>')
        record = json.loads(sys.argv[2])
        saved = append_delivery_record(record)
        print(json.dumps(saved, ensure_ascii=False, indent=2))
        return

    if command == 'latest':
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(get_latest_delivery_record(user_id), ensure_ascii=False, indent=2))
        return

    if command == 'get':
        if len(sys.argv) < 3:
            raise SystemExit('usage: python3 delivery_status_store_mock.py get <request-id>')
        print(json.dumps(get_delivery_record_by_request_id(sys.argv[2]), ensure_ascii=False, indent=2))
        return

    if command == 'list':
        user_id = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
        print(json.dumps(list_delivery_records(user_id, limit), ensure_ascii=False, indent=2))
        return

    raise SystemExit(f'unknown command: {command}')


if __name__ == '__main__':
    main()
