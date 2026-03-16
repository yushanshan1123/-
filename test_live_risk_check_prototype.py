#!/usr/bin/env python3
import json
import subprocess
import sys


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main():
    tests = [
        {
            "name": "valid_pair_ok",
            "args": ['python3', 'binance_connector_prototype.py', 'BTCUSDT'],
            "expect": ['"status": "ok"', '"sourceBinanceStatus": "ok"']
        },
        {
            "name": "invalid_pair_error",
            "args": ['python3', 'binance_connector_prototype.py', 'FAKEUSDT'],
            "expect": ['"status": "error"']
        },
        {
            "name": "live_risk_valid",
            "args": ['python3', 'live_risk_check_prototype.py', '{"pair":"BTCUSDT","side":"short","leverage":10,"positionSize":"未提供","stopLoss":null,"plannedHoldingTime":"短线","thesis":"涨太多了，想吃一波回调"}'],
            "expect": ['【开仓前风险检查】', '风险等级']
        },
        {
            "name": "live_risk_invalid_pair_logic_fallback",
            "args": ['python3', 'live_risk_check_prototype.py', '{"pair":"FAKEUSDT","side":"short","leverage":10,"positionSize":"未提供","stopLoss":null,"plannedHoldingTime":"短线","thesis":"涨太多了，想吃一波回调"}'],
            "expect": ['当前 Binance 实时结构数据不可用', '风险等级']
        }
    ]

    failed = []
    for t in tests:
        code, out, err = run(t['args'])
        ok = code == 0 and all(x in out for x in t['expect'])
        print(f"TEST {t['name']}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            failed.append({"name": t['name'], "code": code, "stdout": out, "stderr": err})

    if failed:
        print("\nFAILED DETAILS:")
        for f in failed:
            print(json.dumps(f, ensure_ascii=False, indent=2))
        sys.exit(1)

    print("\nALL TESTS PASSED")


if __name__ == '__main__':
    main()
