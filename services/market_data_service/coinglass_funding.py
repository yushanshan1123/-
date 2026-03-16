import json
import os
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE = 'https://open-api-v3.coinglass.com'
DEFAULT_PATH = '/api/futures/funding_rates_chart'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def pair_to_symbol(pair: str) -> str:
    pair = (pair or '').upper().strip()
    if pair.endswith('USDT'):
        return pair[:-4]
    return pair


def funding_bias_from_rate(rate):
    if rate is None:
        return None
    if rate > 0.0001:
        return 'long_crowded'
    if rate < -0.0001:
        return 'short_crowded'
    return 'neutral'


def build_error(pair: str, error_code: str, error_message: str, funding_rate=None, funding_bias=None, status='error'):
    return {
        'pair': pair,
        'fundingRate': funding_rate,
        'fundingBias': funding_bias,
        'timestamp': utc_now_iso(),
        'status': status,
        'errorCode': error_code,
        'errorMessage': error_message,
    }


def fetch_json(path: str, params: dict, api_key: str):
    url = f"{BASE}{path}?{urlencode(params)}"
    req = Request(url, headers={
        'accept': 'application/json',
        'User-Agent': 'xinbi-funding-service/0.1',
        'CG-API-KEY': api_key,
    })
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def extract_funding_rate(payload):
    if isinstance(payload, dict):
        data = payload.get('data', payload)
        if isinstance(data, list) and data:
            item = data[-1]
            if isinstance(item, dict):
                for key in ('fundingRate', 'rate', 'value'):
                    if key in item:
                        try:
                            return float(item[key])
                        except Exception:
                            return None
        if isinstance(data, dict):
            for key in ('fundingRate', 'rate', 'value'):
                if key in data:
                    try:
                        return float(data[key])
                    except Exception:
                        return None
    return None


def get_coinglass_funding(pair: str):
    pair = (pair or '').upper().strip()
    if not pair:
        return build_error(pair, 'INVALID_INPUT', 'pair is required')

    api_key = os.getenv('COINGLASS_API_KEY') or os.getenv('COINGLASS_APIKEY')
    if not api_key:
        return build_error(pair, 'UPSTREAM_ERROR', 'missing_coinglass_api_key')

    symbol = pair_to_symbol(pair)
    try:
        payload = fetch_json(DEFAULT_PATH, {'symbol': symbol, 'timeType': 'h1'}, api_key)
        funding_rate = extract_funding_rate(payload)
        funding_bias = funding_bias_from_rate(funding_rate)
        if funding_rate is None and funding_bias is None:
            return build_error(pair, 'PARSE_ERROR', 'funding data unavailable or unparseable', status='error')
        status = 'ok' if funding_rate is not None and funding_bias is not None else 'partial'
        result = {
            'pair': pair,
            'fundingRate': funding_rate,
            'fundingBias': funding_bias,
            'timestamp': utc_now_iso(),
            'status': status,
        }
        if status == 'partial':
            result['errorCode'] = 'PARSE_ERROR'
            result['errorMessage'] = 'partial funding parse'
        return result
    except HTTPError as e:
        code = 'UPSTREAM_TIMEOUT' if e.code == 504 else 'UPSTREAM_ERROR'
        return build_error(pair, code, f'coinglass_http_{e.code}')
    except (URLError, TimeoutError) as e:
        return build_error(pair, 'UPSTREAM_TIMEOUT', str(e))
    except json.JSONDecodeError as e:
        return build_error(pair, 'PARSE_ERROR', str(e))
    except Exception as e:
        return build_error(pair, 'UNKNOWN_ERROR', str(e))
