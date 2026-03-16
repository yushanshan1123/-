from repositories.delivery_status_repository import append_delivery_record, update_delivery_record_status
from delivery_result_schema import build_delivery_result

ALLOWED_STATUS_TRANSITIONS = {
    'queued': {'sent', 'failed'},
    'sent': {'delivered', 'failed'},
    'delivered': set(),
    'failed': set(),
    'mock_sent': set(),
}


def can_transition_delivery_status(current_status: str, next_status: str) -> bool:
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
    return next_status in allowed



def queue_delivery_record(payload: dict):
    request_id = payload.get('requestId')
    if not request_id:
        raise ValueError('requestId is required for queued delivery record')

    record = build_delivery_result(
        ok=True,
        delivery_status='queued',
        delivery_channel=payload.get('channel'),
        target_user_id=payload.get('targetUserId'),
        request_id=request_id,
        trace_id=payload.get('traceId'),
        payload=payload,
        provider_message_id=None,
        mock_message_id=None,
    )
    append_delivery_record(record)
    return record



def transition_delivery_status(record: dict, next_status: str, provider_message_id: str | None = None):
    current_status = record.get('deliveryStatus')
    if not can_transition_delivery_status(current_status, next_status):
        raise ValueError(f'unsupported delivery status transition: {current_status} -> {next_status}')

    request_id = record.get('requestId')
    if not request_id:
        raise ValueError('requestId is required for delivery status transition')

    updated = update_delivery_record_status(
        request_id=request_id,
        delivery_status=next_status,
        provider_message_id=provider_message_id,
    )
    if updated is None:
        raise ValueError(f'delivery record not found: {request_id}')
    return updated
