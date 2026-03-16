#!/usr/bin/env python3
import json

from services.skill_runtime_service import handle_skill_runtime_request


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    invalid_shape = handle_skill_runtime_request('not-a-dict')
    assert_true(invalid_shape['ok'] is False, '非法 request 形状应失败')
    assert_true(invalid_shape['error'] == 'INVALID_INPUT', '非法 request 形状应返回 INVALID_INPUT')
    cases.append('invalid_request_shape')

    unsupported = handle_skill_runtime_request({'action': 'foo', 'payload': {}, 'context': {}})
    assert_true(unsupported['ok'] is False, '不支持 action 应失败')
    assert_true(unsupported['error'] == 'UNSUPPORTED_ACTION', '不支持 action 应返回 UNSUPPORTED_ACTION')
    cases.append('unsupported_action')

    missing_pair = handle_skill_runtime_request({'action': 'snapshot', 'payload': {}, 'context': {}})
    assert_true(missing_pair['ok'] is False, 'snapshot 缺 pair 应失败')
    assert_true(missing_pair['error'] == 'INVALID_INPUT', 'snapshot 缺 pair 应返回 INVALID_INPUT')
    cases.append('snapshot_missing_pair')

    invalid_pair = handle_skill_runtime_request({'action': 'snapshot', 'payload': {'pair': 'btc-usdt'}, 'context': {}})
    assert_true(invalid_pair['ok'] is False, 'snapshot 非法 pair 格式应失败')
    assert_true(invalid_pair['error'] == 'INVALID_INPUT', 'snapshot 非法 pair 格式应返回 INVALID_INPUT')
    cases.append('snapshot_invalid_pair_format')

    invalid_side = handle_skill_runtime_request({
        'action': 'risk_check',
        'payload': {'pair': 'BTCUSDT', 'side': 'hold'},
        'context': {}
    })
    assert_true(invalid_side['ok'] is False, 'risk_check 非法 side 应失败')
    assert_true(invalid_side['error'] == 'INVALID_INPUT', 'risk_check 非法 side 应返回 INVALID_INPUT')
    cases.append('risk_check_invalid_side')

    invalid_leverage = handle_skill_runtime_request({
        'action': 'risk_check',
        'payload': {'pair': 'BTCUSDT', 'side': '做空', 'leverage': 0},
        'context': {}
    })
    assert_true(invalid_leverage['ok'] is False, 'risk_check 非法 leverage 应失败')
    assert_true(invalid_leverage['error'] == 'INVALID_INPUT', 'risk_check 非法 leverage 应返回 INVALID_INPUT')
    cases.append('risk_check_invalid_leverage')

    invalid_event = handle_skill_runtime_request({
        'action': 'alert_to_review',
        'payload': {'event': {'symbol': 'BTC'}},
        'context': {}
    })
    assert_true(invalid_event['ok'] is False, 'alert_to_review 缺 pair 应失败')
    assert_true(invalid_event['error'] == 'INVALID_INPUT', 'alert_to_review 缺 pair 应返回 INVALID_INPUT')
    cases.append('alert_to_review_missing_event_pair')

    invalid_listing_time = handle_skill_runtime_request({
        'action': 'alert_to_review',
        'payload': {'event': {'symbol': 'BTC', 'pair': 'BTCUSDT', 'listingTime': ''}},
        'context': {}
    })
    assert_true(invalid_listing_time['ok'] is False, 'alert_to_review 空 listingTime 应失败')
    assert_true(invalid_listing_time['error'] == 'INVALID_INPUT', 'alert_to_review 空 listingTime 应返回 INVALID_INPUT')
    cases.append('alert_to_review_invalid_listing_time')

    missing_plan = handle_skill_runtime_request({'action': 'risk_to_record', 'payload': {}, 'context': {'userId': 'telegram:6482140148'}})
    assert_true(missing_plan['ok'] is False, 'risk_to_record 缺 plan 应失败')
    assert_true(missing_plan['error'] == 'INVALID_INPUT', 'risk_to_record 缺 plan 应返回 INVALID_INPUT')
    cases.append('risk_to_record_missing_plan')

    invalid_result = handle_skill_runtime_request({
        'action': 'record_to_review',
        'payload': {'result': 'tp'},
        'context': {}
    })
    assert_true(invalid_result['ok'] is False, 'record_to_review 非法 result 应失败')
    assert_true(invalid_result['error'] == 'INVALID_INPUT', 'record_to_review 非法 result 应返回 INVALID_INPUT')
    cases.append('record_to_review_invalid_result')

    long_review_note = handle_skill_runtime_request({
        'action': 'record_to_review',
        'payload': {'result': 'loss', 'reviewNote': 'a' * 501},
        'context': {}
    })
    assert_true(long_review_note['ok'] is False, 'record_to_review 超长 reviewNote 应失败')
    assert_true(long_review_note['error'] == 'INVALID_INPUT', 'record_to_review 超长 reviewNote 应返回 INVALID_INPUT')
    cases.append('record_to_review_review_note_too_long')

    no_record = handle_skill_runtime_request({
        'action': 'record_to_review',
        'payload': {'result': 'loss'},
        'context': {'userId': 'nonexistent-user'}
    })
    assert_true(no_record['ok'] is False, '无记录时应失败')
    assert_true(no_record['error'] == 'NO_RECORD_FOUND', '无记录时应透传 NO_RECORD_FOUND')
    cases.append('record_to_review_no_record_found')

    success = handle_skill_runtime_request({
        'action': 'risk_check',
        'payload': {
            'pair': 'BTCUSDT',
            'side': '做空',
            'leverage': 10,
            'position_size': '未提供',
            'holding': '短线',
            'reason': '涨太多了，想吃一波回调'
        },
        'context': {
            'channel': 'telegram',
            'userId': 'telegram:6482140148'
        }
    })
    assert_true(success['ok'] is True, '合法 risk_check 请求应成功')
    assert_true(success['runtimeMeta']['action'] == 'risk_check', '成功请求应返回正确 action')
    assert_true('data' in success and 'riskResult' in success['data'], '成功请求应返回 riskResult')
    cases.append('risk_check_success')

    print(json.dumps({
        'ok': True,
        'validatedCases': cases,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
