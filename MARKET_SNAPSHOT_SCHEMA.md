# MARKET_SNAPSHOT_SCHEMA.md

## 项目名称
新币合约交易冷静器 2.1

## Day 3 目标
设计统一的 `MarketSnapshot` 数据结构，让 Skill 以后不再直接面对 Binance、Coinglass、GMGN 等原始数据，而只读取一个统一对象。

这份文档解决的问题是：

> 同一个交易对当前的市场状态，后端到底应该以什么结构交给 Skill？

---

## 一、为什么要有 MarketSnapshot
如果没有统一结构，后面会出现几个问题：

1. Skill 会直接依赖每个数据源的原始字段
2. 不同来源字段命名不统一
3. 一旦某个来源断掉，Skill 很难优雅降级
4. 新币提醒、速评、风控、复盘会各自拼数据，越来越乱

所以必须统一成一个对象：

> **MarketSnapshot = 某个交易对在某个时刻的统一市场状态快照**

---

## 二、MarketSnapshot 的设计原则

### 原则 1：Skill 只读统一字段
Skill 不应区分：
- 这个值来自 Binance
- 那个值来自 Coinglass
- 那个值来自 GMGN

这些差异应该由后端处理。

### 原则 2：先支持 MVP 主骨架
Day 3 先把第一版必需字段定清楚，不强求所有增强层都完整。

### 原则 3：每个快照都必须带时间
快照没有时间，就没有复盘价值。

### 原则 4：每个快照都必须带来源状态
因为不是所有来源每次都能成功返回。

---

## 三、MarketSnapshot 顶层结构
建议统一对象长这样：

```json
{
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "marketType": "futures",
  "snapshotTime": "2026-03-11T16:00:00Z",
  "price": 0.1234,
  "change24h": 18.2,
  "high24h": 0.14,
  "low24h": 0.09,
  "volume24h": 120000000,
  "longShortRatio": 1.34,
  "openInterest": 245000000,
  "topTraderLongShortRatio": 0.91,
  "fundingRate": null,
  "fundingBias": null,
  "liquidationRiskZone": null,
  "liquidationRiskDistance": null,
  "smartMoneyObserved": null,
  "smartMoneyBias": null,
  "smartMoneyConfidence": null,
  "sourceBinanceStatus": "ok",
  "sourceCoinglassStatus": "missing",
  "sourceGmgnStatus": "missing",
  "marketMood": null,
  "structureSummary": null,
  "riskSummary": null
}
```

---

## 四、字段分层说明

---

## A. 标识层字段
这些字段用于确定这是“哪个市场的哪一刻快照”。

### 1. symbol
- 类型：string
- 含义：币种代码，例如 `LOBSTER`
- 必需性：P0
- 用途：
  - 提醒消息
  - 速评标题
  - 风控标的识别

### 2. pair
- 类型：string
- 含义：交易对，例如 `LOBSTERUSDT`
- 必需性：P0
- 用途：
  - 数据查询主键
  - 风控目标标识

### 3. marketType
- 类型：string
- 建议值：`spot` / `futures`
- 必需性：P1
- 用途：
  - 区分是现货快照还是合约快照

### 4. snapshotTime
- 类型：string
- 格式：ISO 8601 UTC
- 必需性：P0
- 用途：
  - 风控时点记录
  - 复盘使用
  - 日志与回溯

---

## B. Binance 行情层字段
这些是 MVP 第一版必须重点支持的核心行情字段。

### 5. price
- 类型：number
- 含义：当前价格
- 必需性：P0
- 用途：
  - 提醒中展示价格
  - 风控中判断位置
  - 记录开仓时刻价格

### 6. change24h
- 类型：number
- 含义：24h 涨跌幅
- 必需性：P0
- 用途：
  - 判断热度
  - 判断当前是否剧烈波动

### 7. high24h
- 类型：number
- 含义：24h 最高价
- 必需性：P1
- 用途：
  - 判断是否接近高点区域

### 8. low24h
- 类型：number
- 含义：24h 最低价
- 必需性：P1
- 用途：
  - 判断波动下沿

### 9. volume24h
- 类型：number
- 含义：24h 成交量
- 必需性：P1
- 用途：
  - 判断热度是否有量支撑

---

## C. Binance 合约结构层字段
这部分是风控的主骨架。

### 10. longShortRatio
- 类型：number
- 含义：多空持仓人数比
- 必需性：P0
- 用途：
  - 判断普通账户偏多还是偏空
  - 判断是否情绪拥挤

### 11. openInterest
- 类型：number
- 含义：合约持仓量（Open Interest）
- 必需性：P0
- 用途：
  - 判断当前波动是否伴随仓位扩张
  - 判断是否有真实博弈

### 12. topTraderLongShortRatio
- 类型：number
- 含义：大户持仓多空比
- 必需性：P0
- 用途：
  - 判断大资金方向
  - 判断用户计划是否与大户方向冲突

---

## D. Coinglass 情绪层字段
这部分不是 MVP 第一版主骨架，但已经为增强层预留。

### 13. fundingRate
- 类型：number | null
- 含义：当前资金费率
- 必需性：P1
- 用途：
  - 判断多头 / 空头是否过热

### 14. fundingBias
- 类型：string | null
- 建议值：
  - `long_crowded`
  - `short_crowded`
  - `neutral`
- 必需性：P2（可后端派生）
- 用途：
  - 让 Skill 更快读懂市场情绪

### 15. liquidationRiskZone
- 类型：string | null
- 含义：清算热力风险区描述
- 建议值示例：
  - `above_price_high_density`
  - `below_price_high_density`
  - `neutral`
- 必需性：P2
- 用途：
  - 判断是否接近危险清算带

### 16. liquidationRiskDistance
- 类型：string / number / null
- 含义：当前价格距离风险区的描述或距离值
- 必需性：P2
- 用途：
  - 提醒“当前容易被扫”的位置风险

---

## E. GMGN 聪明钱层字段
这层作为增强层保留。

### 17. smartMoneyObserved
- 类型：boolean | null
- 含义：是否观察到聪明钱信号
- 必需性：P2
- 用途：
  - 判断是否已有更快资金提前布局

### 18. smartMoneyBias
- 类型：string | null
- 建议值：
  - `early_positioning_detected`
  - `unclear`
  - `possible_exit`
- 必需性：P2
- 用途：
  - 判断当前是不是后手进场风险

### 19. smartMoneyConfidence
- 类型：string | null
- 建议值：
  - `low`
  - `medium`
  - `high`
- 必需性：P2
- 用途：
  - 告诉 Skill 这一层判断有多可靠

---

## F. 来源状态层字段
这是必须保留的一层。

### 20. sourceBinanceStatus
- 类型：string
- 建议值：
  - `ok`
  - `partial`
  - `error`
  - `missing`
- 必需性：P0
- 用途：
  - 告诉 Skill Binance 数据是否完整

### 21. sourceCoinglassStatus
- 类型：string
- 建议值：同上
- 必需性：P1
- 用途：
  - 告诉 Skill Coinglass 是否在线

### 22. sourceGmgnStatus
- 类型：string
- 建议值：同上
- 必需性：P1
- 用途：
  - 告诉 Skill GMGN 是否在线

---

## G. 摘要层字段（建议）
这层不是原始数据，而是后端算好的“给 Skill 用的便捷结论”。

### 23. marketMood
- 类型：string | null
- 含义：市场情绪摘要
- 示例：
  - `retail_long_heavy`
  - `retail_short_heavy`
  - `mixed`
- 必需性：P1
- 用途：
  - Skill 输出时更自然

### 24. structureSummary
- 类型：string | null
- 含义：结构摘要
- 示例：
  - `retail long-heavy, whale bias slightly long`
- 必需性：P1
- 用途：
  - 风控输出中的“市场状态摘要”

### 25. riskSummary
- 类型：string | null
- 含义：快速风险摘要
- 示例：
  - `do not chase without stop-loss`
- 必需性：P1
- 用途：
  - 提醒消息 / 风控消息快速输出

---

## 五、MVP 第一版最小字段集
Day 3 先定清楚最小可运行字段。

### P0 最小可运行版本
```json
{
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "snapshotTime": "2026-03-11T16:00:00Z",
  "price": 0.1234,
  "change24h": 18.2,
  "longShortRatio": 1.34,
  "openInterest": 245000000,
  "topTraderLongShortRatio": 0.91,
  "sourceBinanceStatus": "ok"
}
```

只要这个对象能稳定产出，MVP 风控主骨架就可以跑起来。

---

## 六、字段优先级

### P0：MVP 必须
- symbol
- pair
- snapshotTime
- price
- change24h
- longShortRatio
- openInterest
- topTraderLongShortRatio
- sourceBinanceStatus

### P1：建议第一版补上
- marketType
- high24h
- low24h
- volume24h
- sourceCoinglassStatus
- sourceGmgnStatus
- marketMood
- structureSummary
- riskSummary

### P2：后续增强
- fundingRate
- fundingBias
- liquidationRiskZone
- liquidationRiskDistance
- smartMoneyObserved
- smartMoneyBias
- smartMoneyConfidence

---

## 七、MarketSnapshot 在 Skill 中的使用方式

### 1. 用于提醒
提醒消息中最少会读取：
- symbol
- pair
- price
- change24h
- riskSummary

### 2. 用于新币速评
最少会读取：
- price
- change24h
- volume24h（如有）
- marketMood（如有）

### 3. 用于开仓前风险检查
最少会读取：
- price
- change24h
- longShortRatio
- openInterest
- topTraderLongShortRatio
- structureSummary（如有）

### 4. 用于交易计划记录
记录时至少保存：
- price
- change24h
- longShortRatio
- openInterest
- topTraderLongShortRatio
- snapshotTime

---

## 八、数据缺失时的统一降级规则

### 情况 1：只有 P0 字段
系统可正常运行 MVP 风控。

### 情况 2：没有 longShortRatio / OI / 大户多空比
只能做基础行情判断，不能说自己做了结构分析。

### 情况 3：sourceBinanceStatus != ok
Skill 必须明确说：

> 当前 Binance 实时结构数据不可用，以下判断仅基于部分行情或一般逻辑。

### 情况 4：Coinglass / GMGN 缺失
不影响主骨架，但要写清楚：

> 当前未包含资金费率 / 聪明钱层。

---

## 九、Day 3 完成标志
满足以下条件，即视为 Day 3 完成：

- 已经定义清楚 `MarketSnapshot` 顶层结构
- 已经定义 P0 最小字段集
- 已经区分 Binance / Coinglass / GMGN / 摘要层 / 状态层
- 已经明确 Skill 如何读取该对象
- 已经明确数据缺失时如何降级

---

## 十、下一步
Day 4 进入：

**用户提醒配置（UserAlertConfig）与新币事件流（ListingEvent）设计**
