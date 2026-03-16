from datetime import datetime, timezone
from typing import Dict, Any
from uuid import uuid4

from services.skill_runtime_service import handle_skill_runtime_request


def utc_compact_ts() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def generate_request_id(prefix: str = 'req') -> str:
    return f"{prefix}-{utc_compact_ts()}-{uuid4().hex[:8]}"


def build_context(
    channel: str | None = None,
    user_id: str | None = None,
    source: str | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Dict[str, Any]:
    context: Dict[str, Any] = {}
    if channel:
        context['channel'] = channel
    if user_id:
        context['userId'] = user_id
    if source:
        context['source'] = source
    context['requestId'] = request_id or generate_request_id('req')
    context['traceId'] = trace_id or context['requestId']
    return context


def adapt_external_call(action: str, payload: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = dict(context or {})
    if not context.get('requestId'):
        context['requestId'] = generate_request_id('req')
    if not context.get('traceId'):
        context['traceId'] = context['requestId']
    request = {
        'action': action,
        'payload': payload or {},
        'context': context,
    }
    return handle_skill_runtime_request(request)


def adapt_telegram_runtime_call(
    action: str,
    payload: Dict[str, Any] | None = None,
    user_id: str | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Dict[str, Any]:
    context = build_context(
        channel='telegram',
        user_id=user_id,
        source='runtime_adapter_service.telegram',
        request_id=request_id,
        trace_id=trace_id,
    )
    return adapt_external_call(action, payload=payload, context=context)
