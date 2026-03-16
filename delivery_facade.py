import os
from typing import Dict, Any

from delivery_facade_mock import simulate_channel_delivery
from openclaw_message_delivery_adapter import send_via_openclaw_message

FALLBACK_ERRORS = {
    'NOT_CONFIGURED',
}


def should_use_real_adapter() -> bool:
    return os.getenv('XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY') == '1'


def should_fallback_to_mock(result: Dict[str, Any]) -> bool:
    return result.get('ok') is False and result.get('error') in FALLBACK_ERRORS


def deliver_channel_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    正式 facade 名称占位层。
    当前默认回落到 mock delivery。
    若显式打开真实 adapter 开关，则先走 openclaw message adapter；
    当 adapter 返回可回退错误时，再回落到 mock。
    """
    if not should_use_real_adapter():
        return simulate_channel_delivery(payload)

    real_result = send_via_openclaw_message(payload)
    if should_fallback_to_mock(real_result):
        return simulate_channel_delivery(payload)
    return real_result
