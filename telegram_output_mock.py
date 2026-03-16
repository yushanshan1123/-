#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any


def render_telegram_payload(notification_output: Dict[str, Any]) -> Dict[str, Any]:
    title = notification_output.get('title') or ''
    message = notification_output.get('message') or ''
    full_text = f"{title}\n\n{message}".strip()

    buttons = []
    if '速评' in title:
        buttons = [[
            {'text': '查看风控', 'callback_data': 'xinbi:go:risk', 'style': 'primary'},
            {'text': '忽略', 'callback_data': 'xinbi:ignore', 'style': 'danger'},
        ]]
    elif '风控' in title:
        buttons = [[
            {'text': '记录这笔计划', 'callback_data': 'xinbi:record', 'style': 'success'},
            {'text': '忽略', 'callback_data': 'xinbi:ignore', 'style': 'danger'},
        ]]

    return {
        'channel': 'telegram',
        'targetUserId': notification_output.get('targetUserId'),
        'message': full_text,
        'buttons': buttons,
        'requestId': notification_output.get('requestId'),
        'traceId': notification_output.get('traceId'),
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 telegram_output_mock.py <notification-output-json>')
    notification_output = json.loads(sys.argv[1])
    payload = render_telegram_payload(notification_output)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
