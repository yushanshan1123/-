import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE = 'https://fapi.binance.com'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fetch_json(path: str, params: dict):
    url = f"{BASE}{path}?{urlencode(params)}"
    req = Request(url, headers={'User-Agent': 'xinbi-approx-heatmap/0.1'})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def build_error(pair: str, error_code: str, error_message: str):
    return {
        'pair': pair,
        'liquidationRiskZone': None,
        'liquidationRiskDistance': None,
        'timestamp': utc_now_iso(),
        'status': 'error',
        'errorCode': error_code,
        'errorMessage': error_message,
        'mode': 'approx',
    }


def get_approx_liquidation_risk(pair: str):
    """Free approximation of a "liquidation heatmap risk band".

    This does NOT try to replicate paid liquidation heatmaps.
    It produces a simple risk band based on recent volatility (7d, 1h klines)
    and current price. Output is intended for MVP/contest demo when paid
    heatmap APIs are unavailable.

    Returns:
      liquidationRiskZone: {lower, upper, basis, note}
      liquidationRiskDistance: {toLowerPct, toUpperPct}
      status: ok|partial|error
      mode: approx
    """
    pair = (pair or '').upper().strip()
    if not pair:
        return build_error(pair, 'INVALID_INPUT', 'pair is required')

    try:
        # Pull 7d of 1h klines (168 hours)
        klines = fetch_json('/fapi/v1/klines', {
            'symbol': pair,
            'interval': '1h',
            'limit': 168,
        })
        if not isinstance(klines, list) or len(klines) < 24:
            return build_error(pair, 'UPSTREAM_ERROR', 'insufficient kline data')

        highs, lows, closes = [], [], []
        for k in klines:
            if not isinstance(k, list) or len(k) < 5:
                continue
            highs.append(to_float(k[2]))
            lows.append(to_float(k[3]))
            closes.append(to_float(k[4]))

        highs = [x for x in highs if x is not None]
        lows = [x for x in lows if x is not None]
        closes = [x for x in closes if x is not None]

        if len(closes) < 24:
            return build_error(pair, 'PARSE_ERROR', 'unparseable kline closes')

        price = closes[-1]
        week_high = max(highs) if highs else None
        week_low = min(lows) if lows else None

        # Volatility proxy: average true range-like on closes (very simplified)
        diffs = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0.0

        # Risk band width: combine avg_diff with a small % floor
        floor = price * 0.01  # 1% floor
        band = max(avg_diff * 3.0, floor)  # 3x avg hourly move, minimum 1%

        # Two-layer idea:
        # - "near" band = price ± band (short-term sweep risk)
        # - "far" band  = 7d high/low (where large sweeps/liquidations are more likely to cluster)
        near_lower = max(price - band, 0)
        near_upper = price + band

        # Default output uses the FAR band to avoid overly tight ranges in demo.
        lower = week_low if week_low is not None else near_lower
        upper = week_high if week_high is not None else near_upper

        to_lower_pct = (price - lower) / price if price else None
        to_upper_pct = (upper - price) / price if price else None

        return {
            'pair': pair,
            'liquidationRiskZone': {
                'lower': round(lower, 8),
                'upper': round(upper, 8),
                'basis': '7d_range_high_low',
                'note': 'Free approximation: using 7d high/low as the primary risk band (wider). Not a true liquidation heatmap.',
                'nearBand': {
                    'lower': round(near_lower, 8),
                    'upper': round(near_upper, 8),
                    'basis': '3x_avg_1h_move_floor_1pct',
                }
            },
            'liquidationRiskDistance': {
                'toLowerPct': round(to_lower_pct, 6) if to_lower_pct is not None else None,
                'toUpperPct': round(to_upper_pct, 6) if to_upper_pct is not None else None,
            },
            'timestamp': utc_now_iso(),
            'status': 'ok',
            'mode': 'approx',
        }

    except HTTPError as e:
        return build_error(pair, 'UPSTREAM_ERROR', f'binance_http_{e.code}')
    except (URLError, TimeoutError) as e:
        return build_error(pair, 'UPSTREAM_TIMEOUT', str(e))
    except json.JSONDecodeError as e:
        return build_error(pair, 'PARSE_ERROR', str(e))
    except Exception as e:
        return build_error(pair, 'UNKNOWN_ERROR', str(e))
