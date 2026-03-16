# 参赛提交内容（可直接复制填写）

## 作品名称
合约冷静器（Contract Calmness Check）

## 一句话简介
面向普通合约用户的“先冷静再开仓”助手：自动拉取 Binance 永续关键结构数据 + 资金费率，并结合链上项目可靠性（Binance Web3 token info + audit）输出冷静结论与可执行的 TP1/TP2/SL 计划。

## 解决什么问题
- 普通用户看不懂/不想看太多指标，容易情绪化开仓。
- 新/小盘项目常见“套壳/高集中度/高波动”，需要先做项目可靠性快检。

## 核心能力（亮点）
1) **合约冷静器输出模板（适中版）**：项目快检 → 合约结构 → 冷静结论 → 入场/止损/止盈/减仓
2) **资金费率来自 Binance 永续（premiumIndex）**：不依赖付费数据源
3) **“清算热力”降级为免费风险带近似**：用 7d 1h 波动带给出上下风险区间
4) **项目可靠性 token-check**：自动调用 Binance Web3 公共接口，获取 token meta/dynamic/audit
5) **自动搜索官网版合约**：输入 ticker/名称，优先选带官网链接的候选，减少人工确认成本

## 数据来源
- Binance Futures 公共接口（24hr、globalLongShortAccountRatio、openInterest、topLongShortPositionRatio、topLongShortAccountRatio、premiumIndex、klines）
- Binance Web3 公共接口（token search / token meta info / token dynamic info / token audit）

## 如何运行（最小复现）
### 环境
- Python 3.11+（建议 3.12 也可）

### 命令示例
1) 合约快照（永续结构）
```bash
python3 xinbi_cli.py snapshot RIVERUSDT
```

2) 项目可靠性（自动搜索候选）
```bash
python3 xinbi_cli.py token-check --keyword river --chain-ids 56,1,8453,CT_501
```

3) 项目可靠性（指定官网版合约）
```bash
python3 xinbi_cli.py token-check --chain-id 56 --contract 0xda7ad9dea9397cffddae2f8a052b82f1484252b3
```

4) 风控/冷静评分（带红线拦截）
```bash
python3 xinbi_cli.py risk-check --pair RIVERUSDT --side short --leverage 5 --position-size 100 --stop-loss 24.95 --thesis "反弹挂空"
```

## Demo/演示建议（录屏脚本）
1) 输入：`riverusdt`
2) 系统自动：token-search 找到官网版合约 → token-check 输出集中度/审计结果
3) 系统自动：snapshot 输出合约结构+funding+风险带
4) 最终输出：适中版模板（含 TP1/TP2/SL + 减仓规则）

## 风险提示（必填）
本工具为信息整理与风险提示用途，不构成任何投资建议。数字资产价格波动剧烈，交易需自担风险。

## 参赛者信息（你填写）
- X/Twitter：
- 作品链接（GitHub/打包文件链接）：
- 演示视频链接：
- 联系方式：

