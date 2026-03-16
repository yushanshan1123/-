#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from services.risk_check_service import run_risk_check

RECORDS_PATH = Path("/home/ubuntu/.openclaw/workspace/trade_review_records.json")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_records():
    if not RECORDS_PATH.exists():
        return []
    return json.loads(RECORDS_PATH.read_text())


def save_records(records):
    RECORDS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2))


def next_trade_id(records) -> str:
    return f"trade_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{len(records)+1:03d}"


def create_trade_review_record(user_id: str, risk_output: Dict[str, Any]) -> Dict[str, Any]:
    plan = risk_output["plan"]
    snapshot = risk_output["marketSnapshot"]
    now = utc_now_iso()
    records = load_records()
    trade_id = next_trade_id(records)

    record = {
        "tradeId": trade_id,
        "userId": user_id,
        "symbol": snapshot.get("symbol"),
        "pair": plan.get("pair"),
        "side": plan.get("side"),
        "leverage": plan.get("leverage"),
        "positionSize": plan.get("positionSize"),
        "thesis": plan.get("thesis"),
        "stopLoss": plan.get("stopLoss"),
        "plannedHoldingTime": plan.get("plannedHoldingTime"),
        "result": "open",
        "reviewNote": "",
        "snapshotPrice": snapshot.get("price"),
        "snapshotChange24h": snapshot.get("change24h"),
        "snapshotLongShortRatio": snapshot.get("longShortRatio"),
        "snapshotOpenInterest": snapshot.get("openInterest"),
        "snapshotTopTraderLongShortRatio": snapshot.get("topTraderLongShortRatio"),
        "snapshotTime": snapshot.get("snapshotTime"),
        "createdAt": now,
        "updatedAt": now,
    }
    records.append(record)
    save_records(records)
    return record


def build_record_confirmation(record: Dict[str, Any]) -> str:
    lines = [
        "【交易计划已记录】",
        "",
        "我已经把这笔计划记下来了：",
        f"- 交易ID：{record.get('tradeId')}",
        f"- 标的：{record.get('pair')}",
        f"- 方向：{record.get('side')}",
        f"- 杠杆：{record.get('leverage')}",
        f"- 仓位：{record.get('positionSize') or '未提供'}",
        f"- 理由：{record.get('thesis') or '未提供'}",
        "",
        "后续你做完这单时，可以直接回复：",
        "- 复盘这笔计划",
        "- 帮我复盘刚刚那单",
    ]
    return "\n".join(lines)


def simulate_risk_to_record(user_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    risk_output = run_risk_check(plan)
    record = create_trade_review_record(user_id, risk_output)
    confirmation = build_record_confirmation(record)
    return {
        "riskCheck": risk_output,
        "userAction": "记录这笔计划",
        "tradeReviewRecord": record,
        "recordConfirmation": confirmation,
    }


def main():
    if len(sys.argv) > 1:
        payload = json.loads(sys.argv[1])
        user_id = payload.get("userId", "telegram:6482140148")
        plan = payload["plan"]
    else:
        user_id = "telegram:6482140148"
        plan = {
            "pair": "BTCUSDT",
            "side": "做空",
            "leverage": 10,
            "position_size": "未提供",
            "holding": "短线",
            "reason": "涨太多了，想吃一波回调",
        }
    result = simulate_risk_to_record(user_id, plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
