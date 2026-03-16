from datetime import datetime, timezone
from typing import Dict, Any

from repositories.record_repository import create_record


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def create_trade_review_record(user_id: str, risk_output: Dict[str, Any]) -> Dict[str, Any]:
    plan = risk_output['plan']
    snapshot = risk_output['marketSnapshot']
    now = utc_now_iso()

    record = {
        'userId': user_id,
        'symbol': snapshot.get('symbol'),
        'pair': plan.get('pair'),
        'side': plan.get('side'),
        'leverage': plan.get('leverage'),
        'positionSize': plan.get('positionSize'),
        'thesis': plan.get('thesis'),
        'stopLoss': plan.get('stopLoss'),
        'plannedHoldingTime': plan.get('plannedHoldingTime'),
        'result': 'open',
        'reviewNote': '',
        'snapshotPrice': snapshot.get('price'),
        'snapshotChange24h': snapshot.get('change24h'),
        'snapshotLongShortRatio': snapshot.get('longShortRatio'),
        'snapshotOpenInterest': snapshot.get('openInterest'),
        'snapshotTopTraderLongShortRatio': snapshot.get('topTraderLongShortRatio'),
        'snapshotTime': snapshot.get('snapshotTime'),
        'createdAt': now,
        'updatedAt': now,
    }
    return create_record(record)
