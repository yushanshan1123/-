#!/usr/bin/env python3
import json
import os

from services.market_data_service import get_coinglass_funding


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = []

    invalid = get_coinglass_funding('')
    assert_true(invalid['status'] == 'error', '空 pair 应报错')
    assert_true(invalid['errorCode'] == 'INVALID_INPUT', '空 pair 应返回 INVALID_INPUT')
    cases.append('invalid_input')

    has_key = bool(os.getenv('COINGLASS_API_KEY') or os.getenv('COINGLASS_APIKEY'))
    missing = get_coinglass_funding('BTCUSDT')
    if not has_key:
        assert_true(missing['status'] == 'error', '缺 key 时应报错')
        assert_true(missing['errorMessage'] == 'missing_coinglass_api_key', '缺 key 时应返回明确错误')
        cases.append('missing_api_key')
    else:
        assert_true(missing['pair'] == 'BTCUSDT', '有 key 时至少应返回对应 pair')
        cases.append('with_api_key_path_executed')

    print(json.dumps({'ok': True, 'validatedCases': cases}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
