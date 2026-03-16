from typing import Dict, Any

from services.market_data_service import get_market_snapshot
from services.risk_check_service import run_risk_check


def format_pct(v):
    if v is None:
        return '未知'
    sign = '+' if v > 0 else ''
    return f'{sign}{v}%'


def build_structure_summary(snapshot: Dict[str, Any]) -> str:
    lsr = snapshot.get('longShortRatio')
    top = snapshot.get('topTraderLongShortRatio')
    parts = []

    if lsr is None:
        parts.append('普通账户情绪未知')
    elif lsr > 1.1:
        parts.append('普通账户偏多')
    elif lsr < 0.9:
        parts.append('普通账户偏空')
    else:
        parts.append('普通账户中性附近')

    if snapshot.get('openInterest') is not None:
        parts.append('市场仍有持仓博弈')

    if top is None:
        parts.append('大户方向未知')
    elif top > 1.05:
        parts.append('大户偏多')
    elif top < 0.95:
        parts.append('大户偏空')
    else:
        parts.append('大户中性附近')

    return '，'.join(parts)


def build_alert_message(event: Dict[str, Any], snapshot: Dict[str, Any]) -> str:
    lines = [
        '【新币公告提醒】',
        '',
        'Binance 刚发布了新币上线公告：',
        f"- 币种：{event.get('symbol')}",
        f"- 交易对：{event.get('pair')}",
        f"- 上线时间：{event.get('listingTime')}",
        '',
        '当前参考：',
        f"- 价格：{snapshot.get('price') if snapshot.get('price') is not None else '未知'}",
        f"- 24h涨跌：{format_pct(snapshot.get('change24h'))}",
        f"- 市场结构：{build_structure_summary(snapshot)}",
        '',
        '先别急着冲。',
        '如果你只是想先看懂它，回复【速评】。',
        '如果你已经想开仓，回复【风控】。',
        '',
        '回复：',
        '- 速评',
        '- 风控',
        '- 忽略',
    ]
    return '\n'.join(lines)


def build_quick_review(event: Dict[str, Any], snapshot: Dict[str, Any]) -> str:
    pair = event.get('pair')
    symbol = event.get('symbol')
    change24h = snapshot.get('change24h')
    lsr = snapshot.get('longShortRatio')
    top = snapshot.get('topTraderLongShortRatio')

    if change24h is None:
        heat = '当前热度数据不完整，先别急着下结论。'
    elif change24h > 10:
        heat = '当前涨幅已经不低，市场注意力明显偏热。'
    elif change24h > 3:
        heat = '当前有一定热度，但还不算极端。'
    else:
        heat = '当前价格波动还不算特别夸张。'

    if lsr is not None and lsr > 1.1:
        crowd = '普通账户当前偏多。'
    elif lsr is not None and lsr < 0.9:
        crowd = '普通账户当前偏空。'
    else:
        crowd = '普通账户情绪暂时没有明显单边。'

    if top is not None and top > 1.05:
        whale = '大户方向偏多。'
    elif top is not None and top < 0.95:
        whale = '大户方向偏空。'
    else:
        whale = '大户方向暂时没有明显单边。'

    lines = [
        '【新币速评】',
        '',
        '1. 一句话结论',
        f"- {symbol}（{pair}）当前更适合先观察结构和热度，不适合因为公告就直接追。",
        '',
        '2. 为什么会被关注',
        f"- 因为 Binance 公告本身就会带来短期关注度，{symbol} 这类新上币事件天然容易吸引情绪流量。",
        '',
        '3. 当前市场参考',
        f"- 当前价格：{snapshot.get('price') if snapshot.get('price') is not None else '未知'}",
        f"- 24h涨跌：{format_pct(change24h)}",
        f"- 情绪结构：{crowd}{whale}",
        '',
        '4. 主要风险',
        f"- {heat}",
        '- 公告带来的关注，不等于现在就是舒服位置。',
        '- 如果没有明确计划，最容易从“想先看看”变成“情绪追单”。',
        '',
        '5. 普通人现在最该先看什么',
        '- 先看热度是不是已经过头',
        '- 再看结构是否支持继续追',
        '- 如果你已经想开仓，下一步更适合先做风控，而不是直接下单',
    ]
    return '\n'.join(lines)


def simulate_alert_to_risk(event: Dict[str, Any], user_plan: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = get_market_snapshot(event['pair'])
    alert_message = build_alert_message(event, snapshot)
    risk_result = run_risk_check(user_plan)
    return {
        'listingEvent': event,
        'marketSnapshot': snapshot,
        'alertMessage': alert_message,
        'userAction': '风控',
        'riskCheck': risk_result,
    }


def simulate_alert_to_review(event: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = get_market_snapshot(event['pair'])
    alert_message = build_alert_message(event, snapshot)
    quick_review = build_quick_review(event, snapshot)
    return {
        'listingEvent': event,
        'marketSnapshot': snapshot,
        'alertMessage': alert_message,
        'userAction': '速评',
        'quickReview': quick_review,
    }
