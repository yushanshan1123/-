# TRADE_REVIEW_RECORD_SCHEMA.md

## 项目名称
新币合约交易冷静器 2.1

## Day 7 目标
定义交易计划记录（`TradeReviewRecord`）的统一结构，让系统在用户完成风控后，可以把这笔计划保存下来，供后续复盘使用。

这份文档解决的问题是：

> **当用户说“记录这笔计划”时，系统到底应该存什么。**

---

## 一、为什么必须有 TradeReviewRecord
如果没有 `TradeReviewRecord`，后面会出现这些问题：

1. 风控结果看完就没了
2. 用户后面说“帮我复盘那单”，系统没有依据
3. 无法回看开仓时的市场结构
4. 无法比较“计划”和“执行”是否一致

所以 MVP 第一版必须至少支持“交易计划记录”。

---

## 二、TradeReviewRecord 顶层结构
建议统一对象如下：

```json
{
  "tradeId": "trade_20260311_001",
  "userId": "telegram:6482140148",
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "side": "short",
  "leverage": 10,
  "positionSize": "medium",
  "thesis": "涨太多了，想吃一波回调",
  "stopLoss": null,
  "plannedHoldingTime": "short-term",
  "result": "open",
  "reviewNote": "",
  "snapshotPrice": 0.1234,
  "snapshotChange24h": 18.2,
  "snapshotLongShortRatio": 1.34,
  "snapshotOpenInterest": 245000000,
  "snapshotTopTraderLongShortRatio": 0.91,
  "snapshotTime": "2026-03-11T16:00:00Z",
  "createdAt": "2026-03-11T16:01:00Z",
  "updatedAt": "2026-03-11T16:01:00Z"
}
```

---

## 三、字段说明

---

## A. 记录标识字段

### 1. tradeId
- 类型：string
- 含义：交易记录唯一 ID
- 示例：`trade_20260311_001`
- 必需性：P0
- 用途：
  - 唯一标识一条交易计划记录
  - 后续复盘时精确读取

### 2. userId
- 类型：string
- 含义：该记录属于哪个用户
- 必需性：P0

---

## B. 交易计划字段

### 3. symbol
- 类型：string
- 含义：币种代码
- 必需性：P0

### 4. pair
- 类型：string
- 含义：交易对
- 必需性：P0

### 5. side
- 类型：string
- 建议值：
  - `long`
  - `short`
- 必需性：P0

### 6. leverage
- 类型：number
- 含义：杠杆倍数
- 必需性：P0

### 7. positionSize
- 类型：string / number
- 含义：仓位大小
- 必需性：P0

### 8. thesis
- 类型：string
- 含义：开仓理由 / 交易逻辑
- 必需性：P0

### 9. stopLoss
- 类型：string / number / null
- 含义：止损位置
- 必需性：P0

### 10. plannedHoldingTime
- 类型：string
- 含义：预期持仓时间
- 示例：`short-term` / `intraday` / `swing`
- 必需性：P1

---

## C. 交易结果字段
MVP 第一版先做轻量版本。

### 11. result
- 类型：string
- 建议值：
  - `open`
  - `win`
  - `loss`
  - `break_even`
- 必需性：P1
- 用途：
  - 标记这笔记录目前是未结束还是已结束

### 12. reviewNote
- 类型：string
- 含义：用户自己的补充说明
- 必需性：P2

---

## D. 市场快照字段
这部分是这条记录最有价值的地方。

### 13. snapshotPrice
- 类型：number
- 含义：记录这笔计划时的价格
- 必需性：P0

### 14. snapshotChange24h
- 类型：number
- 含义：记录时的 24h 涨跌幅
- 必需性：P0

### 15. snapshotLongShortRatio
- 类型：number
- 含义：记录时的多空持仓人数比
- 必需性：P0

### 16. snapshotOpenInterest
- 类型：number
- 含义：记录时的 OI
- 必需性：P0

### 17. snapshotTopTraderLongShortRatio
- 类型：number
- 含义：记录时的大户持仓多空比
- 必需性：P0

### 18. snapshotTime
- 类型：string
- 含义：记录风控快照的时间
- 必需性：P0

---

## E. 系统时间字段

### 19. createdAt
- 类型：string
- 含义：记录创建时间
- 必需性：P0

### 20. updatedAt
- 类型：string
- 含义：记录更新时间
- 必需性：P0

---

## 四、MVP 第一版最小字段集

```json
{
  "tradeId": "trade_20260311_001",
  "userId": "telegram:6482140148",
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "side": "short",
  "leverage": 10,
  "positionSize": "medium",
  "thesis": "涨太多了，想吃一波回调",
  "stopLoss": null,
  "snapshotPrice": 0.1234,
  "snapshotChange24h": 18.2,
  "snapshotLongShortRatio": 1.34,
  "snapshotOpenInterest": 245000000,
  "snapshotTopTraderLongShortRatio": 0.91,
  "snapshotTime": "2026-03-11T16:00:00Z",
  "createdAt": "2026-03-11T16:01:00Z",
  "updatedAt": "2026-03-11T16:01:00Z"
}
```

---

## 五、MVP 第一版记录时机
建议在以下时机允许写入记录：

### 1. 用户收到风控结论后，主动说：
- 记录这笔计划
- 帮我记下来

### 2. 系统提示用户：
- 是否记录这笔交易计划，方便后续复盘？

---

## 六、记录缺失时的处理规则

### 情况 1：用户计划不完整
如果缺少：
- side
- leverage
- positionSize
- thesis

则不建议直接保存为正式记录，先提示补信息。

### 情况 2：市场快照不完整
如果缺少快照主字段，仍可记录，但要明确：
- 本次记录缺少部分市场结构快照

---

## 七、Day 7（记录部分）完成标志
满足以下条件，即视为 `TradeReviewRecord` 设计完成：

- 已定义记录最小字段集
- 已定义市场快照字段
- 已定义记录时机
- 已定义结果字段
- 已定义缺失记录规则

---

## 八、下一步
与 `RECORD_AND_REVIEW_FLOW.md` 一起使用，形成 MVP 闭环。
