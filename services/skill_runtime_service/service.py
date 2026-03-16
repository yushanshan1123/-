import re
from typing import Dict, Any

from services.skill_entry_service import (
    handle_snapshot_request,
    handle_risk_check_request,
    handle_alert_to_risk_request,
    handle_alert_to_review_request,
    handle_risk_to_record_request,
    handle_record_to_review_request,
)

VALID_ACTIONS = {
    'snapshot',
    'risk_check',
    'alert_to_risk',
    'alert_to_review',
    'risk_to_record',
    'record_to_review',
}

REQUIRED_PAYLOAD_FIELDS = {
    'snapshot': ['pair'],
    'risk_check': ['pair', 'side'],
    'alert_to_risk': ['event', 'plan'],
    'alert_to_review': ['event'],
    'risk_to_record': ['plan'],
    'record_to_review': [],
}

VALID_SIDE_VALUES = {'做多', '多', 'buy', 'long', '做空', '空', 'sell', 'short'}
VALID_REVIEW_RESULTS = {'win', 'loss', 'break_even', 'open'}
KNOWN_DOWNSTREAM_ERRORS = {
    'INVALID_INPUT',
    'PAIR_NOT_FOUND',
    'UPSTREAM_TIMEOUT',
    'UPSTREAM_ERROR',
    'UPSTREAM_PARTIAL_ERROR',
    'PARSE_ERROR',
    'UNKNOWN_ERROR',
    'NO_RECORD_FOUND',
}
PAIR_PATTERN = re.compile(r'^[A-Z0-9]{6,20}$')
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9]{2,10}$')
MAX_REVIEW_NOTE_LENGTH = 500
MAX_LISTING_TIME_LENGTH = 100
MAX_LEVERAGE = 125


def build_runtime_meta(action: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    return {
        'action': action,
        'channel': context.get('channel'),
        'userId': context.get('userId'),
        'source': context.get('source', 'skill_runtime_service'),
        'requestId': context.get('requestId'),
        'traceId': context.get('traceId'),
    }


def error_response(error: str, message: str, action: str, context: Dict[str, Any] | None = None, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    response = {
        'ok': False,
        'error': error,
        'message': message,
        'runtimeMeta': build_runtime_meta(action, context),
    }
    if details:
        response['details'] = details
    return response


def validate_request_shape(request: Any) -> tuple[bool, str | None]:
    if not isinstance(request, dict):
        return False, 'request 必须是对象'
    if 'action' not in request:
        return False, 'request 缺少 action'
    if 'payload' in request and not isinstance(request['payload'], dict):
        return False, 'payload 必须是对象'
    if 'context' in request and not isinstance(request['context'], dict):
        return False, 'context 必须是对象'
    return True, None


def is_valid_pair(value: str) -> bool:
    return bool(PAIR_PATTERN.match(value.upper()))


def is_valid_symbol(value: str) -> bool:
    return bool(SYMBOL_PATTERN.match(value.upper()))


def validate_leverage(value: Any, field_name: str) -> tuple[bool, str | None, Dict[str, Any] | None]:
    if value in [None, '']:
        return True, None, None
    try:
        leverage = float(value)
    except Exception:
        return False, f'{field_name} 必须是数字', {'invalidFields': [field_name]}
    if leverage <= 0:
        return False, f'{field_name} 必须大于 0', {'invalidFields': [field_name]}
    if leverage > MAX_LEVERAGE:
        return False, f'{field_name} 不能大于 {MAX_LEVERAGE}', {'invalidFields': [field_name]}
    return True, None, None


def validate_event_payload(event: Dict[str, Any], action: str) -> tuple[bool, str | None, Dict[str, Any] | None]:
    symbol = str(event.get('symbol') or '').strip()
    pair = str(event.get('pair') or '').strip().upper()
    listing_time = event.get('listingTime')
    if not symbol:
        return False, f'{action} 的 event 缺少有效 symbol', {'missingFields': ['event.symbol']}
    if not is_valid_symbol(symbol):
        return False, f'{action} 的 event.symbol 格式不合法：{symbol}', {'invalidFields': ['event.symbol']}
    if not pair:
        return False, f'{action} 的 event 缺少有效 pair', {'missingFields': ['event.pair']}
    if not is_valid_pair(pair):
        return False, f'{action} 的 event.pair 格式不合法：{pair}', {'invalidFields': ['event.pair']}
    if listing_time is not None:
        listing_time = str(listing_time).strip()
        if not listing_time:
            return False, f'{action} 的 event.listingTime 不能为空字符串', {'invalidFields': ['event.listingTime']}
        if len(listing_time) > MAX_LISTING_TIME_LENGTH:
            return False, f'{action} 的 event.listingTime 长度不能超过 {MAX_LISTING_TIME_LENGTH}', {'invalidFields': ['event.listingTime']}
    return True, None, None


def validate_plan_payload(plan: Dict[str, Any], action: str) -> tuple[bool, str | None, Dict[str, Any] | None]:
    pair = str(plan.get('pair') or plan.get('symbol') or '').strip().upper()
    side = str(plan.get('side') or '').strip().lower()
    if not pair:
        return False, f'{action} 的 plan 缺少有效 pair/symbol', {'missingFields': ['plan.pair']}
    if not is_valid_pair(pair):
        return False, f'{action} 的 plan.pair 格式不合法：{pair}', {'invalidFields': ['plan.pair']}
    if not side:
        return False, f'{action} 的 plan 缺少有效 side', {'missingFields': ['plan.side']}
    if side not in {v.lower() for v in VALID_SIDE_VALUES}:
        return False, f'{action} 的 plan.side 不在支持范围内：{plan.get("side")}', {'invalidFields': ['plan.side']}
    ok, err, details = validate_leverage(plan.get('leverage'), 'plan.leverage')
    if not ok:
        return ok, err, details
    return True, None, None


def validate_payload(action: str, payload: Dict[str, Any]) -> tuple[bool, str | None, Dict[str, Any] | None]:
    missing = [field for field in REQUIRED_PAYLOAD_FIELDS.get(action, []) if field not in payload]
    if missing:
        return False, f"{action} 缺少必填字段：{', '.join(missing)}", {'missingFields': missing}

    if action == 'risk_check':
        pair = str(payload.get('pair') or payload.get('symbol') or '').strip().upper()
        side = str(payload.get('side') or '').strip().lower()
        if not pair:
            return False, 'risk_check 缺少有效 pair/symbol', {'missingFields': ['pair']}
        if not is_valid_pair(pair):
            return False, f'risk_check 的 pair/symbol 格式不合法：{pair}', {'invalidFields': ['pair']}
        if not side:
            return False, 'risk_check 缺少有效 side', {'missingFields': ['side']}
        if side not in {v.lower() for v in VALID_SIDE_VALUES}:
            return False, f"risk_check 的 side 不在支持范围内：{payload.get('side')}", {'invalidFields': ['side']}
        ok, err, details = validate_leverage(payload.get('leverage'), 'leverage')
        if not ok:
            return ok, err, details

    if action == 'snapshot':
        pair = str(payload.get('pair') or '').strip().upper()
        if not pair:
            return False, 'snapshot 缺少有效 pair', {'missingFields': ['pair']}
        if not is_valid_pair(pair):
            return False, f'snapshot 的 pair 格式不合法：{pair}', {'invalidFields': ['pair']}

    if action == 'alert_to_risk':
        event = payload.get('event')
        plan = payload.get('plan')
        if not isinstance(event, dict):
            return False, 'alert_to_risk 的 event 必须是对象', {'invalidFields': ['event']}
        if not isinstance(plan, dict):
            return False, 'alert_to_risk 的 plan 必须是对象', {'invalidFields': ['plan']}
        ok, err, details = validate_event_payload(event, action)
        if not ok:
            return ok, err, details
        ok, err, details = validate_plan_payload(plan, action)
        if not ok:
            return ok, err, details

    if action == 'alert_to_review':
        event = payload.get('event')
        if not isinstance(event, dict):
            return False, 'alert_to_review 的 event 必须是对象', {'invalidFields': ['event']}
        ok, err, details = validate_event_payload(event, action)
        if not ok:
            return ok, err, details

    if action == 'risk_to_record':
        plan = payload.get('plan')
        if not isinstance(plan, dict):
            return False, 'risk_to_record 的 plan 必须是对象', {'invalidFields': ['plan']}
        ok, err, details = validate_plan_payload(plan, action)
        if not ok:
            return ok, err, details

    if action == 'record_to_review':
        result = payload.get('result')
        review_note = payload.get('reviewNote')
        if result is not None and str(result).strip() not in VALID_REVIEW_RESULTS:
            return False, f"record_to_review 的 result 不在支持范围内：{result}", {'invalidFields': ['result']}
        if review_note is not None:
            note = str(review_note)
            if len(note) > MAX_REVIEW_NOTE_LENGTH:
                return False, f'record_to_review 的 reviewNote 长度不能超过 {MAX_REVIEW_NOTE_LENGTH}', {'invalidFields': ['reviewNote']}

    return True, None, None


def normalize_downstream_error(result: Any, action: str, context: Dict[str, Any]) -> Dict[str, Any] | None:
    if not isinstance(result, dict):
        return None

    if 'error' in result and result['error']:
        error = str(result['error'])
        message = str(result.get('message') or result.get('errorMessage') or error)
        details = result.get('details') if isinstance(result.get('details'), dict) else None
        if error in KNOWN_DOWNSTREAM_ERRORS:
            return error_response(error, message, action, context, details)
        return error_response('UNKNOWN_ERROR', message, action, context, {'downstreamError': error})

    snapshot = result.get('marketSnapshot') if isinstance(result.get('marketSnapshot'), dict) else None
    if snapshot and snapshot.get('sourceBinanceStatus') == 'error':
        error = str(snapshot.get('errorCode') or 'UPSTREAM_ERROR')
        message = str(snapshot.get('errorMessage') or '市场快照读取失败')
        if error not in KNOWN_DOWNSTREAM_ERRORS:
            error = 'UPSTREAM_ERROR'
        return error_response(error, message, action, context, {'marketSnapshot': snapshot})

    if result.get('mode') == 'logic_only' and snapshot and snapshot.get('sourceBinanceStatus') == 'error':
        error = str(snapshot.get('errorCode') or 'UPSTREAM_ERROR')
        message = str(snapshot.get('errorMessage') or '实时数据不可用，已退回 logic_only')
        if error not in KNOWN_DOWNSTREAM_ERRORS:
            error = 'UPSTREAM_ERROR'
        return error_response(error, message, action, context, {'marketSnapshot': snapshot, 'mode': 'logic_only'})

    risk_check = result.get('riskCheck') if isinstance(result.get('riskCheck'), dict) else None
    if risk_check:
        nested = normalize_downstream_error(risk_check, action, context)
        if nested:
            return nested

    return None


def handle_skill_runtime_request(request: Dict[str, Any]) -> Dict[str, Any]:
    ok, shape_error = validate_request_shape(request)
    if not ok:
        return error_response('INVALID_INPUT', shape_error or '无效请求', 'unknown', {})

    action = request.get('action')
    payload = request.get('payload') or {}
    context = request.get('context') or {}

    if not isinstance(action, str) or not action.strip():
        return error_response('INVALID_INPUT', 'action 必须是非空字符串', str(action), context)

    if action not in VALID_ACTIONS:
        return error_response('UNSUPPORTED_ACTION', f'暂不支持的 runtime action: {action}', action, context)

    payload_ok, payload_error, details = validate_payload(action, payload)
    if not payload_ok:
        return error_response('INVALID_INPUT', payload_error or 'payload 校验失败', action, context, details)

    try:
        if action == 'snapshot':
            result = handle_snapshot_request(payload['pair'])
        elif action == 'risk_check':
            result = handle_risk_check_request(payload)
        elif action == 'alert_to_risk':
            result = handle_alert_to_risk_request(payload['event'], payload['plan'])
        elif action == 'alert_to_review':
            result = handle_alert_to_review_request(payload['event'])
        elif action == 'risk_to_record':
            user_id = context.get('userId') or payload.get('userId') or 'unknown-user'
            result = handle_risk_to_record_request(user_id, payload['plan'])
        else:
            user_id = context.get('userId') or payload.get('userId')
            result = handle_record_to_review_request(
                payload.get('result', 'loss'),
                payload.get('reviewNote', ''),
                user_id=user_id,
            )
    except KeyError as e:
        return error_response('INVALID_INPUT', f'缺少必要字段：{e.args[0]}', action, context)
    except Exception as e:
        return error_response('UNKNOWN_ERROR', f'runtime 执行失败：{e}', action, context)

    downstream_error = normalize_downstream_error(result, action, context)
    if downstream_error:
        return downstream_error

    return {
        'ok': True,
        'runtimeMeta': build_runtime_meta(action, context),
        'data': result,
    }
