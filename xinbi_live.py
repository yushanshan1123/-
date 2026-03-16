#!/usr/bin/env python3
import json

from services.market_data_service import get_market_snapshot
from services.risk_check_service import normalize_plan_input, assess_risk, build_risk_report, run_risk_check


def run_live_risk_check(plan):
    return run_risk_check(plan)


def run_live_risk_check_json(plan_json: str) -> str:
    plan = json.loads(plan_json)
    result = run_live_risk_check(plan)
    return json.dumps(result, ensure_ascii=False, indent=2)


__all__ = [
    'get_market_snapshot',
    'normalize_plan_input',
    'assess_risk',
    'build_risk_report',
    'run_live_risk_check',
    'run_live_risk_check_json',
]
