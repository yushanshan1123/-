from typing import Dict, Any

from delivery_result_schema import build_delivery_result


SUPPORTED_CHANNELS = {'telegram'}


def build_message_send_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get('channel')
    target_user_id = payload.get('targetUserId')
    message_text = payload.get('message')

    if not channel:
        raise ValueError('channel is required')
    if channel not in SUPPORTED_CHANNELS:
        raise ValueError(f'unsupported channel: {channel}')
    if not target_user_id:
        raise ValueError('targetUserId is required')
    if not message_text:
        raise ValueError('message is required')

    return {
        'action': 'send',
        'channel': channel,
        'target': target_user_id,
        'message': message_text,
    }


def execute_message_send_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    真实 message.send 执行层占位。
    当前仅固定执行层接口形状，后续接入真实发送时优先替换这里。
    """
    return {
        'ok': False,
        'error': 'NOT_IMPLEMENTED',
        'message': 'message.send execution is not implemented yet',
        'request': request,
    }


def map_message_send_result(tool_result: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    provider_message_id = None
    if isinstance(tool_result, dict):
        provider_message_id = (
            tool_result.get('messageId')
            or tool_result.get('message_id')
            or tool_result.get('providerMessageId')
        )

    return build_delivery_result(
        ok=True,
        delivery_status='sent',
        delivery_channel=payload.get('channel'),
        target_user_id=payload.get('targetUserId'),
        request_id=payload.get('requestId'),
        trace_id=payload.get('traceId'),
        payload=payload,
        provider_message_id=provider_message_id,
        mock_message_id=None,
    )


def build_adapter_error(payload: Dict[str, Any], error: str, message: str) -> Dict[str, Any]:
    return build_delivery_result(
        ok=False,
        delivery_status='failed',
        delivery_channel=payload.get('channel'),
        target_user_id=payload.get('targetUserId'),
        request_id=payload.get('requestId'),
        trace_id=payload.get('traceId'),
        payload=payload,
        provider_message_id=None,
        mock_message_id=None,
    ) | {
        'error': error,
        'message': message,
    }


def send_via_openclaw_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    真实发送适配器占位层。
    当前已补齐 request/result/error 映射壳，并抽出独立执行层；
    但尚未实际调用 message.send。
    当未来接入真实发送时，优先替换执行层实现。
    """
    try:
        request = build_message_send_request(payload)
    except ValueError as e:
        return build_adapter_error(payload, 'INVALID_DELIVERY_PAYLOAD', str(e))

    execution = execute_message_send_request(request)
    if execution.get('ok') is True:
        return map_message_send_result(execution, payload)

    return build_adapter_error(
        payload,
        execution.get('error') or 'NOT_CONFIGURED',
        execution.get('message') or 'openclaw message delivery adapter is not configured yet',
    )
