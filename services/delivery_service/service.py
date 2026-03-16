from typing import Dict, Any

from delivery_facade import deliver_channel_payload


def send_channel_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    当前统一走正式命名的 delivery facade。
    facade 内部暂时仍回落到 mock implementation。
    未来真实替换时，优先改 facade 层。
    """
    return deliver_channel_payload(payload)
