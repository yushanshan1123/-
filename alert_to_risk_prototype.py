#!/usr/bin/env python3
import json
import sys

from services.alert_service import simulate_alert_to_risk


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

    result = simulate_alert_to_risk(event, plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
