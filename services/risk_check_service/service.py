from typing import List, Dict, Any

from services.market_data_service import get_market_snapshot


def normalize_plan_input(plan: Dict[str, Any]) -> Dict[str, Any]:
    pair = str(plan.get('pair') or plan.get('symbol') or '').upper().strip()
    side = str(plan.get('side') or '').lower().strip()
    if side in ['做多', '多', 'buy']:
        side = 'long'
    elif side in ['做空', '空', 'sell']:
        side = 'short'

    return {
        'pair': pair,
        'side': side,
        'leverage': plan.get('leverage'),
        'positionSize': plan.get('positionSize') if 'positionSize' in plan else plan.get('position_size'),
        'stopLoss': plan.get('stopLoss') if 'stopLoss' in plan else plan.get('stop_loss'),
        'plannedHoldingTime': plan.get('plannedHoldingTime') if 'plannedHoldingTime' in plan else plan.get('holding') or plan.get('holding_time'),
        'thesis': plan.get('thesis') or plan.get('reason') or '',
    }


def zh_side(side: str) -> str:
    return '做多' if side == 'long' else '做空' if side == 'short' else str(side)


def is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def format_pct(v):
    if v is None:
        return '未知'
    sign = '+' if v > 0 else ''
    return f'{sign}{v}%'


def summarize_ratio(name: str, v: float, bullish_label: str, bearish_label: str) -> str:
    if v is None:
        return f'{name}：未知'
    if v > 1.1:
        bias = bullish_label
    elif v < 0.9:
        bias = bearish_label
    else:
        bias = '中性附近'
    return f'{name}：{v}（{bias}）'


def compute_cold_score_and_redlines(plan: dict, snapshot: dict):
    """Return (cold_score: int 0-100, redlines: list[str]).

    Cold score is a *calmness* score: higher means safer/less emotional to execute.
    Redlines are hard blocks: when present, prefer to WAIT rather than open immediately.
    """
    score = 100
    redlines: List[str] = []

    # Plan completeness (coldness starts from having a plan)
    if is_missing(plan.get('stopLoss')):
        score -= 25
        redlines.append('缺少止损：先写止损，再谈开仓。')
    if is_missing(plan.get('positionSize')):
        score -= 10
    if is_missing(plan.get('leverage')):
        score -= 10

    # Leverage penalty
    lev = plan.get('leverage')
    try:
        if lev is not None:
            lev = float(lev)
            if lev >= 20:
                score -= 25
                redlines.append('杠杆过高（>=20x）：冷静器建议先降杠杆。')
            elif lev >= 10:
                score -= 15
            elif lev >= 5:
                score -= 8
    except Exception:
        score -= 5

    # Market crowding
    lsr = snapshot.get('longShortRatio')
    if lsr is not None:
        if lsr >= 1.3:
            score -= 10
        elif lsr <= 0.7:
            score -= 10

    # Funding crowding
    fb = snapshot.get('fundingBias')
    side = plan.get('side')
    if fb == 'long_crowded' and side == 'long':
        score -= 18
        redlines.append('资金费率显示多头拥挤：不建议追多，优先等回踩/降杠杆。')
    if fb == 'short_crowded' and side == 'short':
        score -= 18
        redlines.append('资金费率显示空头拥挤：不建议追空，优先等反弹/降杠杆。')

    # Heatmap / risk band proximity (free approx band is OK)
    dist = snapshot.get('liquidationRiskDistance') or {}
    to_lower = dist.get('toLowerPct')
    to_upper = dist.get('toUpperPct')
    try:
        if side == 'long' and to_lower is not None and float(to_lower) <= 0.02:
            score -= 15
            redlines.append('离下方风险带太近（<=2%）：容易被扫，建议等待更好位置。')
        if side == 'short' and to_upper is not None and float(to_upper) <= 0.02:
            score -= 15
            redlines.append('离上方风险带太近（<=2%）：容易被扫，建议等待更好位置。')
    except Exception:
        pass

    # Big trader structure conflict
    top_pos = snapshot.get('topTraderLongShortRatio')
    if side == 'long' and top_pos is not None and top_pos < 0.95:
        score -= 18
        redlines.append('大户持仓结构不支持做多：冷静器建议先观望或等结构修复。')
    if side == 'short' and top_pos is not None and top_pos > 1.05:
        score -= 18
        redlines.append('大户持仓结构不支持做空：冷静器建议先观望或等结构修复。')

    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return int(score), redlines[:3]


def assess_risk(plan: dict, snapshot: dict):
    blocking_conflicts: List[str] = []
    conflicts: List[str] = []
    advice: List[str] = []
    risk_score = 0

    missing_fields = [
        label for label, key in [
            ('开仓理由', 'thesis'),
            ('杠杆倍数', 'leverage'),
            ('仓位大小', 'positionSize'),
            ('止损位置', 'stopLoss'),
        ] if is_missing(plan.get(key))
    ]

    if missing_fields:
        conflicts.append(f"当前计划缺少关键信息：{'、'.join(missing_fields)}。")
        risk_score += 1 if len(missing_fields) == 1 else 2
        advice.append('先把仓位、止损、理由补完整，再决定要不要上单。')

    thesis = str(plan.get('thesis', '')).strip()
    if any(x in thesis for x in ['涨太多', '跌太多', '感觉', '想吃一波回调']):
        conflicts.append('当前开仓理由偏情绪化，更像主观预判，而不是完整交易逻辑。')
        risk_score += 1

    leverage = plan.get('leverage')
    if leverage is not None:
        try:
            leverage = float(leverage)
            if leverage >= 10:
                conflicts.append('杠杆偏高，叠加高波动标的时，容错会明显变差。')
                risk_score += 2
                advice.append('如果真要做，优先降杠杆，不要一上来放大波动。')
            elif leverage >= 5:
                risk_score += 1
        except Exception:
            pass

    status = snapshot.get('sourceBinanceStatus')
    if status == 'ok':
        lsr = snapshot.get('longShortRatio')
        top = snapshot.get('topTraderLongShortRatio')
        oi = snapshot.get('openInterest')
        side = plan.get('side')

        if side == 'long' and lsr is not None and lsr > 1.2:
            conflicts.append('当前普通账户明显偏多，继续追多要警惕情绪拥挤。')
            risk_score += 1
        if side == 'short' and lsr is not None and lsr < 0.9:
            conflicts.append('当前普通账户明显偏空，继续追空要警惕情绪拥挤。')
            risk_score += 1

        if side == 'long' and top is not None and top < 0.95:
            conflicts.append('当前你的方向和大户结构存在冲突：你想做多，但大户没有明显站多。')
            risk_score += 2
        if side == 'short' and top is not None and top > 1.05:
            conflicts.append('当前你的方向和大户结构存在冲突：你想做空，但大户没有明显站空。')
            risk_score += 2

        if oi is not None and oi > 0:
            advice.append('当前市场仍有持仓博弈，别把单边预判当成确定性结论。')
    elif status == 'partial':
        blocking_conflicts.append('当前只接入了部分 Binance 实时数据，本次判断不包含完整结构层分析。')
        risk_score += 1
    else:
        blocking_conflicts.append('当前 Binance 实时结构数据不可用，本次判断只能按 logic-only 方式保守处理。')
        risk_score += 2

    if risk_score <= 1:
        level = '中'
    elif risk_score <= 3:
        level = '高'
    else:
        level = '极高'

    if not advice:
        advice.append('先按计划交易，而不是按情绪交易。')
    advice.append('如果你愿意，我下一步可以把这笔交易计划记录下来，方便后续复盘。')

    final_conflicts = (blocking_conflicts + conflicts)[:3]
    cold_score, redlines = compute_cold_score_and_redlines(plan, snapshot)
    # If there are redlines, treat risk as at least High.
    if redlines and level == '中':
        level = '高'
    return level, final_conflicts, advice[:3], cold_score, redlines


def build_risk_report(plan: dict, snapshot: dict) -> str:
    level, conflicts, advice, cold_score, redlines = assess_risk(plan, snapshot)
    thesis = plan.get('thesis') or '未提供'
    summary = []
    summary.append('【开仓前风险检查】')
    summary.append('')
    summary.append('1. 当前计划摘要')
    summary.append(f"- 标的：{plan.get('pair')}")
    summary.append(f"- 方向：{zh_side(plan.get('side'))}")
    summary.append(f"- 杠杆：{plan.get('leverage')}x" if plan.get('leverage') is not None else '- 杠杆：未提供')
    summary.append(f"- 仓位：{plan.get('positionSize') or '未提供'}")
    summary.append(f"- 止损：{plan.get('stopLoss') or '未提供'}")
    summary.append(f"- 持仓预期：{plan.get('plannedHoldingTime') or '未提供'}")
    summary.append(f"- 开仓理由：{thesis}")
    summary.append('')
    summary.append('2. 市场状态摘要')
    summary.append(f"- 当前价格：{snapshot.get('price') if snapshot.get('price') is not None else '未知'}")
    summary.append(f"- 24h涨跌：{format_pct(snapshot.get('change24h'))}")
    summary.append(f"- {summarize_ratio('多空持仓人数比', snapshot.get('longShortRatio'), '普通账户偏多', '普通账户偏空')}")
    summary.append(f"- 合约持仓量：{snapshot.get('openInterest') if snapshot.get('openInterest') is not None else '未知'}")
    summary.append(f"- {summarize_ratio('大户持仓多空比', snapshot.get('topTraderLongShortRatio'), '大户偏多', '大户偏空')}")
    summary.append('')
    summary.append('3. 冷静评分（0-100）')
    summary.append(f"- {cold_score}")
    if redlines:
        summary.append('- 红线拦截：')
        for r in redlines:
            summary.append(f"  - {r}")
    summary.append('')
    summary.append('4. 核心冲突点')
    for c in conflicts:
        summary.append(f'- {c}')
    summary.append('')
    summary.append('5. 风险等级')
    summary.append(f'- {level}')
    summary.append('')
    summary.append('6. 一句话结论')
    if level == '极高':
        line = '这单现在更像高风险预判单，不建议直接冲。'
    elif level == '高':
        line = '这单不是绝对不能做，但当前结构和计划完整度都不够友好。'
    else:
        line = '这单可以继续观察，但仍应按计划而不是按情绪处理。'
    summary.append(f'- {line}')
    summary.append('')
    summary.append('7. 冷静建议')
    for a in advice:
        summary.append(f'- {a}')
    return '\n'.join(summary)


def run_risk_check(plan: Dict[str, Any]) -> Dict[str, Any]:
    normalized_plan = normalize_plan_input(plan)
    snapshot = get_market_snapshot(normalized_plan['pair'])
    report = build_risk_report(normalized_plan, snapshot)
    level, conflicts, advice, cold_score, redlines = assess_risk(normalized_plan, snapshot)
    return {
        'mode': 'live' if snapshot.get('sourceBinanceStatus') in ['ok', 'partial'] else 'logic_only',
        'plan': normalized_plan,
        'marketSnapshot': snapshot,
        'riskResult': {
            'riskLevel': level,
            'coldScore': cold_score,
            'redlines': redlines,
            'conflicts': conflicts,
            'advice': advice,
        },
        'report': report,
    }
