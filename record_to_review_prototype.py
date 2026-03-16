#!/usr/bin/env python3
import json
import sys

from services.review_service import review_latest_trade


def simulate_record_to_review(result: str = 'loss', review_note: str = ''):
    return review_latest_trade(result, review_note)


def main():
    if len(sys.argv) > 1:
        payload = json.loads(sys.argv[1])
        result = payload.get('result', 'loss')
        review_note = payload.get('reviewNote', '')
    else:
        result = 'loss'
        review_note = '这单最后止损了。'
    output = simulate_record_to_review(result, review_note)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
