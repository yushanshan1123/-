from datetime import datetime, timezone
from typing import Any, Dict


VALID_DELIVERY_STATUSES = {
    'queued',
    'sent',
    'delivered',
    'failed',
    'mock_sent',
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def build_delivery_result(
    *,
    ok: bool,
    delivery_status: str,
    delivery_channel: str | None,
    target_user_id: str | None,
    request_id: str | None,
    trace_id: str | None,
    payload: Dict[str, Any] | None,
    provider_message_id: str | None = None,
    mock_message_id: str | None = None,
    sent_at: str | None = None,
) -> Dict[str, Any]:
    if delivery_status not in VALID_DELIVERY_STATUSES:
        raise ValueError(f'unsupported delivery_status: {delivery_status}')

    return {
        'ok': ok,
        'deliveryStatus': delivery_status,
        'deliveryChannel': delivery_channel,
        'targetUserId': target_user_id,
        'providerMessageId': provider_message_id,
        'mockMessageId': mock_message_id,
        'sentAt': sent_at or utc_now_iso(),
        'requestId': request_id,
        'traceId': trace_id,
        'payload': payload,
    }
