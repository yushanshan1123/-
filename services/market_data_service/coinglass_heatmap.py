import json
import os
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE = 'https://open-api-v3.coinglass.com'
DEFAULT_PATH = '/api/futures/liquidation_heatmap'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def pair_to_symbol(pair: str) -> str:
    pair = (pair or '').upper().strip()
    if pair.endswith('USDT'):
        return pair[:-4]
    return pair


def build_error(pair: str, error_code: str, error_message: str, zone=None, distance=None, status='error'):
    return {
        'pair': pair,
        'liquidationRiskZone': zone,
        'liquidationRiskDistance': distance,
        'timestamp': utc_now_iso(),
        'status': status,
        'errorCode': error_code,
        'errorMessage': error_message,
    }


def fetch_json(path: str, params: dict, api_key: str):
    url = f"{BASE}{path}?{urlencode(params)}"
    req = Request(url, headers={
        'accept': 'application/json',
        'User-Agent': 'xinbi-heatmap-service/0.1',
        'CG-API-KEY': api_key,
    })
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def extract_heatmap_risk(payload):
    # 当前先做保守解析：如果未来拿到稳定 payload，再按真实字段替换。
    if not isinstance(payload, dict):
        return None, None
    data = payload.get('data', payload)
    if isinstance(data, dict):
        zone = data.get('liquidationRiskZone') or data.get('riskZone')
        distance = data.get('liquidationRiskDistance') or data.get('riskDistance')
        return zone, distance
    return None, None


def get_coinglass_heatmap_risk(pair: str):
    pair = (pair or '').upper().strip()
    if not pair:
        return build_error(pair, 'INVALID_INPUT', 'pair is required')

    api_key = os.getenv('COINGLASS_API_KEY') or os.getenv('COINGLASS_APIKEY')
    if not api_key:
        return build_error(pair, 'UPSTREAM_ERROR', 'missing_coinglass_api_key')

    symbol = pair_to_symbol(pair)
    try:
        payload = fetch_json(DEFAULT_PATH, {'symbol': symbol}, api_key)
        zone, distance = extract_heatmap_risk(payload)
        if zone is None and distance is None:
            return build_error(pair, 'PARSE_ERROR', 'heatmap data unavailable or unparseable')
        status = 'ok' if zone is not None and distance is not None else 'partial'
        result = {
            'pair': pair,
            'liquidationRiskZone': zone if zone is not None else 'unknown',
            'liquidationRiskDistance': distance if distance is not None else 'unknown',
            'timestamp': utc_now_iso(),
            'status': status,
        }
        if status == 'partial':
            result['errorCode'] = 'PARSE_ERROR'
            result['errorMessage'] = 'partial heatmap parse'
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
