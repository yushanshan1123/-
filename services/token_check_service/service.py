import json
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fetch_json(url: str, method: str = 'GET', headers: dict | None = None, body: dict | None = None):
    headers = headers or {}
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers.setdefault('Content-Type', 'application/json')
    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode('utf-8'))


def search_token_candidates(keyword: str, chain_ids: str | None = None, limit: int = 5) -> dict:
    keyword = (keyword or '').strip()
    if not keyword:
        return {'status': 'error', 'errorCode': 'INVALID_INPUT', 'errorMessage': 'keyword is required', 'timestamp': utc_now_iso()}

    headers = {
        'Accept-Encoding': 'identity',
        'User-Agent': 'binance-web3/1.0 (xinbi)',
    }
    params = {'keyword': keyword}
    if chain_ids:
        params['chainIds'] = chain_ids
    params['orderBy'] = 'volume24h'

    url = 'https://web3.binance.com/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search?' + urlencode(params)
    try:
        payload = fetch_json(url, headers=headers)
        data = payload.get('data') if isinstance(payload, dict) else None
        if not isinstance(data, list):
            data = []
        # Return top N candidates (keep lightweight)
        cand = []
        for item in data[:limit]:
            cand.append({
                'chainId': item.get('chainId'),
                'name': item.get('name'),
                'symbol': item.get('symbol'),
                'contractAddress': item.get('contractAddress'),
                'volume24h': item.get('volume24h'),
                'liquidity': item.get('liquidity'),
                'marketCap': item.get('marketCap'),
                'percentChange24h': item.get('percentChange24h'),
                'links': item.get('links') or [],
                'tagsInfo': item.get('tagsInfo'),
            })
        return {'status': 'ok', 'timestamp': utc_now_iso(), 'keyword': keyword, 'candidates': cand}
    except Exception as e:
        return {'status': 'error', 'errorCode': 'UPSTREAM_ERROR', 'errorMessage': str(e), 'timestamp': utc_now_iso()}


def run_token_check(chain_id: str, contract_address: str) -> dict:
    """Project reliability MVP using Binance Web3 public endpoints.

    - token meta info
    - token dynamic info (holders/liquidity/top10%)
    - token audit (honeypot/scam/trade risks)

    No API key required.
    """
    chain_id = (chain_id or '').strip()
    contract_address = (contract_address or '').strip()
    if not chain_id or not contract_address:
        return {
            'status': 'error',
            'errorCode': 'INVALID_INPUT',
            'errorMessage': 'chainId and contractAddress are required',
            'timestamp': utc_now_iso(),
        }

    headers = {
        'Accept-Encoding': 'identity',
        'User-Agent': 'binance-web3/1.4 (xinbi)',
    }

    out = {
        'status': 'ok',
        'timestamp': utc_now_iso(),
        'chainId': chain_id,
        'contractAddress': contract_address,
        'tokenMeta': None,
        'tokenDynamic': None,
        'tokenAudit': None,
    }

    # Meta
    try:
        url = 'https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/meta/info?' + urlencode({
            'chainId': chain_id,
            'contractAddress': contract_address,
        })
        out['tokenMeta'] = fetch_json(url, headers=headers)
    except Exception as e:
        out['tokenMeta'] = {'success': False, 'error': str(e)}
        out['status'] = 'partial'

    # Dynamic
    try:
        url = 'https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info?' + urlencode({
            'chainId': chain_id,
            'contractAddress': contract_address,
        })
        out['tokenDynamic'] = fetch_json(url, headers=headers)
    except Exception as e:
        out['tokenDynamic'] = {'success': False, 'error': str(e)}
        out['status'] = 'partial'

    # Audit
    try:
        url = 'https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit'
        body = {
            'binanceChainId': str(chain_id),
            'contractAddress': contract_address,
            'requestId': str(uuid.uuid4()),
        }
        out['tokenAudit'] = fetch_json(url, method='POST', headers={
            **headers,
            'User-Agent': 'binance-web3/1.4 (Skill)',
        }, body=body)
    except Exception as e:
        out['tokenAudit'] = {'success': False, 'error': str(e)}
        out['status'] = 'partial'

    return out
