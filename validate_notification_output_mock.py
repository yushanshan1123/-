#!/usr/bin/env python3
import json

from notification_output_mock import render_notification_from_runtime_result
from scheduler_runtime_entry_mock import handle_scheduler_runtime_request


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    review_runtime = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-review',
        'action': 'alert_to_review',
        'payload': {
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            }
        },
        'requestId': 'sched-review-out-001',
        'traceId': 'trace-review-out-001',
    })
    review_output = render_notification_from_runtime_result(review_runtime)
    assert_true(review_output['title'] == '【新币速评推送】', '速评输出标题应正确')
    assert_true('一句话结论' in review_output['message'], '速评输出应包含速评正文')
    cases.append('render_review_notification')

    risk_runtime = handle_scheduler_runtime_request({
        'jobName': 'listing-alert-risk',
        'action': 'alert_to_risk',
        'payload': {
            'event': {
                'symbol': 'BTC',
                'pair': 'BTCUSDT',
                'listingTime': '2026-03-11 18:00（UTC+8）'
            },
            'plan': {
                'pair': 'BTCUSDT',
                'side': '做空',
                'leverage': 10,
                'position_size': '未提供',
                'holding': '短线',
                'reason': '涨太多了，想吃一波回调'
            }
        },
        'requestId': 'sched-risk-out-001',
        'traceId': 'trace-risk-out-001',
    })
    risk_output = render_notification_from_runtime_result(risk_runtime)
    assert_true(risk_output['title'] == '【新币风控推送】', '风控输出标题应正确')
    assert_true('【开仓前风险检查】' in risk_output['message'], '风控输出应包含风控正文')
    cases.append('render_risk_notification')

    failure_output = render_notification_from_runtime_result({
        'ok': False,
        'error': 'INVALID_INPUT',
        'message': 'bad input',
        'runtimeMeta': {'channel': 'scheduler', 'requestId': 'r1', 'traceId': 't1'}
    })
    assert_true(failure_output['title'] == '【提醒发送失败】', '失败输出标题应正确')
    assert_true(failure_output['message'] == 'bad input', '失败输出应包含错误消息')
    cases.append('render_failure_notification')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
