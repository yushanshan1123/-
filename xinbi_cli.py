#!/usr/bin/env python3
import argparse
import json

from services.skill_entry_service import (
    handle_snapshot_request,
    handle_risk_check_request,
    handle_alert_to_risk_request,
    handle_alert_to_review_request,
    handle_risk_to_record_request,
    handle_record_to_review_request,
)
from services.skill_runtime_service import handle_skill_runtime_request
from services.token_check_service import run_token_check, search_token_candidates


def main():
    parser = argparse.ArgumentParser(description="新币合约交易冷静器 2.1 最小 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot", help="读取 Binance 市场快照")
    snap.add_argument("pair", help="交易对，例如 BTCUSDT")

    risk = sub.add_parser("risk-check", help="执行 live 风控")
    risk.add_argument("--pair", required=True)
    risk.add_argument("--side", required=True)
    risk.add_argument("--leverage", type=float)
    risk.add_argument("--position-size", dest="positionSize")
    risk.add_argument("--stop-loss", dest="stopLoss")
    risk.add_argument("--holding", dest="plannedHoldingTime")
    risk.add_argument("--thesis", default="")
    risk.add_argument("--json", action="store_true", dest="as_json")

    skill = sub.add_parser("skill-risk-check", help="用更接近 Skill 的 JSON 输入执行风控")
    skill.add_argument("payload", help="JSON 字符串，至少包含 pair/side 等字段")

    atr = sub.add_parser("alert-to-risk", help="模拟提醒后进入风控")
    atr.add_argument("payload", help="包含 event/plan 的 JSON 字符串")

    atv = sub.add_parser("alert-to-review", help="模拟提醒后进入速评")
    atv.add_argument("event", help="事件 JSON 字符串")

    rtr = sub.add_parser("risk-to-record", help="模拟风控后记录")
    rtr.add_argument("payload", help="包含 userId/plan 的 JSON 字符串")

    rrev = sub.add_parser("record-to-review", help="模拟记录后复盘")
    rrev.add_argument("payload", help="包含 result/reviewNote 的 JSON 字符串")

    runtime = sub.add_parser("runtime-call", help="模拟正式 skill runtime 调用")
    runtime.add_argument("request", help="包含 action/payload/context 的 JSON 字符串")

    tok = sub.add_parser("token-check", help="项目可靠性检查（Binance Web3 token info + audit）")
    tok.add_argument("--chain-id", dest="chainId", help="链 ID：56(BSC)/8453(Base)/CT_501(Solana)/1(Ethereum)")
    tok.add_argument("--contract", dest="contractAddress", help="合约地址")
    tok.add_argument("--keyword", dest="keyword", help="Token 名称/符号/合约地址（用于自动搜索候选）")
    tok.add_argument("--chain-ids", dest="chainIds", help="搜索限定链IDs，如 56,8453,CT_501")

    args = parser.parse_args()

    if args.command == "snapshot":
        print(json.dumps(handle_snapshot_request(args.pair), ensure_ascii=False, indent=2))
        return

    if args.command == "risk-check":
        plan = {
            "pair": args.pair,
            "side": args.side,
            "leverage": args.leverage,
            "positionSize": args.positionSize,
            "stopLoss": args.stopLoss,
            "plannedHoldingTime": args.plannedHoldingTime,
            "thesis": args.thesis,
        }
        result = handle_risk_check_request(plan)
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["report"])
        return

    if args.command == "skill-risk-check":
        payload = json.loads(args.payload)
        print(json.dumps(handle_risk_check_request(payload), ensure_ascii=False, indent=2))
        return

    if args.command == "alert-to-risk":
        payload = json.loads(args.payload)
        print(json.dumps(handle_alert_to_risk_request(payload['event'], payload['plan']), ensure_ascii=False, indent=2))
        return

    if args.command == "alert-to-review":
        event = json.loads(args.event)
        print(json.dumps(handle_alert_to_review_request(event), ensure_ascii=False, indent=2))
        return

    if args.command == "risk-to-record":
        payload = json.loads(args.payload)
        user_id = payload.get('userId', 'telegram:6482140148')
        print(json.dumps(handle_risk_to_record_request(user_id, payload['plan']), ensure_ascii=False, indent=2))
        return

    if args.command == "record-to-review":
        payload = json.loads(args.payload)
        result = payload.get('result', 'loss')
        review_note = payload.get('reviewNote', '')
        print(json.dumps(handle_record_to_review_request(result, review_note), ensure_ascii=False, indent=2))
        return

    if args.command == "runtime-call":
        request = json.loads(args.request)
        print(json.dumps(handle_skill_runtime_request(request), ensure_ascii=False, indent=2))
        return

    if args.command == "token-check":
        # If contract+chain provided, run full check.
        if args.chainId and args.contractAddress:
            print(json.dumps(run_token_check(args.chainId, args.contractAddress), ensure_ascii=False, indent=2))
            return

        # Otherwise, search candidates by keyword.
        if args.keyword:
            print(json.dumps(search_token_candidates(args.keyword, args.chainIds), ensure_ascii=False, indent=2))
            return

        raise SystemExit('token-check requires either (--chain-id AND --contract) or --keyword')


if __name__ == "__main__":
    main()
