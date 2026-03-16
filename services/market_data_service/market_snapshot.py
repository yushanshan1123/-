from .binance_connector import get_binance_market_core
from .coinglass_funding import get_coinglass_funding
from .coinglass_heatmap import get_coinglass_heatmap_risk
from .approx_liquidation_risk import get_approx_liquidation_risk


def pair_to_symbol(pair: str) -> str:
    if pair.endswith('USDT'):
        return pair[:-4]
    return pair


def to_market_snapshot(core: dict, funding: dict | None = None, heatmap: dict | None = None):
    funding = funding or {}
    heatmap = heatmap or {}
    return {
        'symbol': pair_to_symbol(core['pair']),
        'pair': core['pair'],
        'snapshotTime': core['timestamp'],
        'price': core['price'],
        'change24h': core['change24h'],
        'longShortRatio': core['longShortRatio'],
        'openInterest': core['openInterest'],
        'topTraderLongShortRatio': core['topTraderLongShortRatio'],
        'topTraderLongShortAccountRatio': core.get('topTraderLongShortAccountRatio'),
        'sourceBinanceStatus': core['status'],

        # Funding: prefer Binance perpetual funding (always available when pair is supported);
        # fall back to Coinglass funding connector when Binance value is missing.
        'fundingRate': core.get('fundingRate') if core.get('fundingRate') is not None else funding.get('fundingRate'),
        'fundingBias': core.get('fundingBias') if core.get('fundingBias') is not None else funding.get('fundingBias'),
        'sourceCoinglassStatus': funding.get('status'),

        'liquidationRiskZone': heatmap.get('liquidationRiskZone'),
        'liquidationRiskDistance': heatmap.get('liquidationRiskDistance'),
        'sourceHeatmapStatus': heatmap.get('status'),
    }


def get_market_snapshot(pair: str):
    core = get_binance_market_core(pair)

    # Funding: keep Coinglass connector as optional fallback, but Binance is preferred.
    funding = get_coinglass_funding(pair)

    # Heatmap: try Coinglass first; if unavailable, use a free approximation band.
    heatmap = get_coinglass_heatmap_risk(pair)
    if (heatmap or {}).get('status') != 'ok':
        heatmap = get_approx_liquidation_risk(pair)

    return to_market_snapshot(core, funding, heatmap)
