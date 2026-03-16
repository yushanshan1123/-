from typing import Dict, Any

from services.market_data_service import get_market_snapshot
from services.risk_check_service import run_risk_check
from services.alert_service import simulate_alert_to_risk, simulate_alert_to_review
from services.record_service import create_trade_review_record
from services.review_service import review_latest_trade


def handle_snapshot_request(pair: str) -> Dict[str, Any]:
    return get_market_snapshot(pair)


def handle_risk_check_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    return run_risk_check(payload)


def handle_alert_to_risk_request(event: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    return simulate_alert_to_risk(event, plan)


def handle_alert_to_review_request(event: Dict[str, Any]) -> Dict[str, Any]:
    return simulate_alert_to_review(event)


def handle_risk_to_record_request(user_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    risk_output = run_risk_check(plan)
    record = create_trade_review_record(user_id, risk_output)
    return {
        'riskCheck': risk_output,
        'userAction': '记录这笔计划',
        'tradeReviewRecord': record,
    }


def handle_record_to_review_request(result: str = 'loss', review_note: str = '', user_id: str | None = None) -> Dict[str, Any]:
    return review_latest_trade(result, review_note, user_id=user_id)
