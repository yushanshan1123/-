from typing import Dict, Any

from repositories.record_repository import get_latest_record, update_record


def side_zh(side: str) -> str:
    return '做多' if side == 'long' else '做空' if side == 'short' else side


def bias_text(v, long_label='偏多', short_label='偏空'):
    if v is None:
        return '未知'
    if v > 1.1:
        return long_label
    if v < 0.9:
        return short_label
    return '中性附近'


def update_record_result(trade_id: str, result: str, review_note: str = '') -> Dict[str, Any] | None:
    patch = {'result': result}
    if review_note:
        patch['reviewNote'] = review_note
    return update_record(trade_id, patch)


def build_review(record: Dict[str, Any]) -> str:
    result = record.get('result', 'open')
    if result == 'win':
        result_text = '止盈'
    elif result == 'loss':
        result_text = '止损'
    elif result == 'break_even':
        result_text = '保本'
    else:
        result_text = '持有中'

    thesis_ok = '有一定逻辑，但还不够完整。'
    if '涨太多' in (record.get('thesis') or ''):
        thesis_ok = '有直觉依据，但更像提前预判，而不是完整结构确认。'

    execution = '如果你按计划执行了止损 / 止盈，执行层面是合格的。'
    if record.get('stopLoss') in [None, '', '未提供']:
        execution = '这单最大的问题之一，是计划阶段就没有明确止损。'

    if result == 'loss':
        biggest = '你在结构没有明显转弱前，就用高杠杆提前预判了方向。'
        fix = '下次不要只因为“涨太多了”就直接空，先等更明确的结构信号。'
    elif result == 'win':
        biggest = '这次你能赚钱，不代表这个入场逻辑已经足够稳健。'
        fix = '下次把止损和仓位也提前定清楚，避免把一次正确变成长期习惯。'
    elif result == 'break_even':
        biggest = '这单说明你有警觉，但计划阶段仍然不够完整。'
        fix = '下次把触发条件写得更具体，别只靠感觉和位置预判。'
    else:
        biggest = '当前这笔交易还没结束，过早定论意义不大。'
        fix = '等结果明确后，再做完整复盘会更有价值。'

    lines = [
        '【交易复盘】',
        '',
        '1. 原始计划回顾',
        f"- 标的：{record.get('pair')}",
        f"- 方向：{side_zh(record.get('side'))}",
        f"- 杠杆：{record.get('leverage')}x",
        f"- 仓位：{record.get('positionSize') or '未提供'}",
        f"- 理由：{record.get('thesis') or '未提供'}",
        '',
        '2. 当时市场状态',
        f"- 价格：{record.get('snapshotPrice')}",
        f"- 24h涨跌：{record.get('snapshotChange24h')}%",
        f"- 多空持仓人数比：{bias_text(record.get('snapshotLongShortRatio'))}",
        f"- 合约持仓量：{record.get('snapshotOpenInterest')}",
        f"- 大户持仓多空比：{bias_text(record.get('snapshotTopTraderLongShortRatio'))}",
        '',
        '3. 结果',
        f"- {result_text}",
        '',
        '4. 复盘结论',
        f"- 原始逻辑是否成立：{thesis_ok}",
        f"- 执行是否到位：{execution}",
        f"- 本次最大问题：{biggest}",
        f"- 下次最该改的一点：{fix}",
    ]
    return '\n'.join(lines)


def review_latest_trade(result: str = 'loss', review_note: str = '', user_id: str | None = None) -> Dict[str, Any]:
    latest = get_latest_record(user_id)
    if not latest:
        return {'error': 'NO_RECORD_FOUND'}
    updated = update_record_result(latest['tradeId'], result, review_note)
    review = build_review(updated)
    return {
        'userAction': '复盘这笔计划',
        'tradeReviewRecord': updated,
        'reviewOutput': review,
    }
