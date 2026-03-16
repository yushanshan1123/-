#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any


def render_notification_from_runtime_result(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    runtime_meta = runtime_result.get('runtimeMeta', {})
    data = runtime_result.get('data', {})

    if runtime_result.get('ok') is not True:
        return {
            'deliveryChannel': runtime_meta.get('channel') or 'mock-output',
            'targetUserId': runtime_meta.get('userId'),
            'title': '【提醒发送失败】',
            'message': runtime_result.get('message') or runtime_result.get('error') or '未知错误',
            'requestId': runtime_meta.get('requestId'),
            'traceId': runtime_meta.get('traceId'),
        }

    user_action = data.get('userAction')
    if user_action == '速评':
        title = '【新币速评推送】'
        message = data.get('quickReview') or data.get('alertMessage') or '无可用内容'
    elif user_action == '风控':
        title = '【新币风控推送】'
        risk = data.get('riskCheck', {})
        message = risk.get('report') or data.get('alertMessage') or '无可用内容'
    else:
        title = '【运行结果推送】'
        message = json.dumps(data, ensure_ascii=False, indent=2)

    return {
        'deliveryChannel': runtime_meta.get('channel') or 'mock-output',
        'targetUserId': runtime_meta.get('userId'),
        'title': title,
        'message': message,
        'requestId': runtime_meta.get('requestId'),
        'traceId': runtime_meta.get('traceId'),
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 notification_output_mock.py <runtime-result-json>')
    runtime_result = json.loads(sys.argv[1])
    output = render_notification_from_runtime_result(runtime_result)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
