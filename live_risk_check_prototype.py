#!/usr/bin/env python3
import json
import sys

from xinbi_live import run_live_risk_check


def main():
    if len(sys.argv) > 1:
        plan = json.loads(sys.argv[1])
    else:
        plan = {
            "pair": "BTCUSDT",
            "side": "short",
            "leverage": 10,
            "positionSize": "未提供",
            "stopLoss": None,
            "plannedHoldingTime": "短线",
            "thesis": "涨太多了，想吃一波回调",
        }
    result = run_live_risk_check(plan)
    print(result["report"])


if __name__ == "__main__":
    main()
