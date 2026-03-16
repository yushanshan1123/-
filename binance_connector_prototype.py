#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE = "https://fapi.binance.com"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_json(path: str, params: dict):
    url = f"{BASE}{path}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "xinbi-connector-prototype/0.1"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pair_to_symbol(pair: str) -> str:
    if pair.endswith("USDT"):
        return pair[:-4]
    return pair


def get_binance_market_core(pair: str):
    timestamp = utc_now_iso()
    if not pair or not isinstance(pair, str):
        return {
            "pair": pair,
            "price": None,
            "change24h": None,
            "longShortRatio": None,
            "openInterest": None,
            "topTraderLongShortRatio": None,
            "timestamp": timestamp,
            "status": "error",
            "errorCode": "INVALID_INPUT",
            "errorMessage": "pair is required",
        }

    pair = pair.upper().strip()
    fields = {
        "pair": pair,
        "price": None,
        "change24h": None,
        "longShortRatio": None,
        "openInterest": None,
        "topTraderLongShortRatio": None,
        "timestamp": timestamp,
        "status": "error",
    }
    errors = []

    try:
        ticker = fetch_json("/fapi/v1/ticker/24hr", {"symbol": pair})
        fields["price"] = to_float(ticker.get("lastPrice"))
        fields["change24h"] = to_float(ticker.get("priceChangePercent"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
        errors.append(f"ticker24hr:{e}")

    try:
        gls = fetch_json("/futures/data/globalLongShortAccountRatio", {"symbol": pair, "period": "5m", "limit": 1})
        if isinstance(gls, list) and gls:
            fields["longShortRatio"] = to_float(gls[0].get("longShortRatio"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
        errors.append(f"globalLongShortAccountRatio:{e}")

    try:
        oi = fetch_json("/fapi/v1/openInterest", {"symbol": pair})
        fields["openInterest"] = to_float(oi.get("openInterest"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
        errors.append(f"openInterest:{e}")

    try:
        top = fetch_json("/futures/data/topLongShortPositionRatio", {"symbol": pair, "period": "5m", "limit": 1})
        if isinstance(top, list) and top:
            fields["topTraderLongShortRatio"] = to_float(top[0].get("longShortRatio"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
        errors.append(f"topLongShortPositionRatio:{e}")

    core_keys = ["price", "change24h", "longShortRatio", "openInterest", "topTraderLongShortRatio"]
    present = sum(fields[k] is not None for k in core_keys)

    if present == len(core_keys):
        fields["status"] = "ok"
    elif fields["price"] is not None or fields["change24h"] is not None:
        fields["status"] = "partial"
    else:
        fields["status"] = "error"

    if errors:
        fields["errorCode"] = "UPSTREAM_PARTIAL_ERROR" if fields["status"] != "error" else "UPSTREAM_ERROR"
        fields["errorMessage"] = "; ".join(errors)

    return fields


def to_market_snapshot(core: dict):
    return {
        "symbol": pair_to_symbol(core["pair"]),
        "pair": core["pair"],
        "snapshotTime": core["timestamp"],
        "price": core["price"],
        "change24h": core["change24h"],
        "longShortRatio": core["longShortRatio"],
        "openInterest": core["openInterest"],
        "topTraderLongShortRatio": core["topTraderLongShortRatio"],
        "sourceBinanceStatus": core["status"],
    }


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    core = get_binance_market_core(pair)
    snapshot = to_market_snapshot(core)
    print(json.dumps({"connector": core, "marketSnapshot": snapshot}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
