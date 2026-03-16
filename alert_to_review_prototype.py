#!/usr/bin/env python3
import json
import sys

from services.alert_service import simulate_alert_to_review


def main():
    if len(sys.argv) > 1:
        event = json.loads(sys.argv[1])
    else:
        event = {
            'symbol': 'BTC',
            'pair': 'BTCUSDT',
            'listingTime': '2026-03-11 18:00（UTC+8）',
        }
    result = simulate_alert_to_review(event)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
