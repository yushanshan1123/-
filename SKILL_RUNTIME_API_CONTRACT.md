# SKILL_RUNTIME_API_CONTRACT.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **新币合约交易冷静器 2.1 在正式 Skill runtime / 后端入口层的最小输入输出契约。**

它解决的问题是：
- runtime 层到底接什么结构
- action 怎么命名
- payload 应该长什么样
- context 应该带什么
- response 应该如何统一包装
- 错误怎么表达

这份契约的目标不是一步做到很复杂，
而是先把 MVP 第一版真正需要的 runtime 调用格式定清楚。

---

## 一、当前契约适用范围
当前契约适用于：

- 本地 `skill_runtime_service`
- 后续正式 Skill runtime 入口
- 后续 API / 调度入口的内部调用封装

当前不代表：
- 已经存在正式 HTTP API
- 已经存在跨服务 RPC
- 已经存在正式消息总线

所以这份文档现在更准确的定位是：

> **runtime 入口协议草案的第一版正式化文档。**

---

## 二、统一请求结构
所有 runtime 调用统一使用一个 request 对象：

```json
{
  "action": "risk_check",
  "payload": {},
  "context": {}
}
```

### 1. `action`
表示要执行的 runtime 动作。

当前必须是字符串。

### 2. `payload`
表示该 action 的业务输入。

当前必须是对象。

### 3. `context`
表示调用上下文。

当前必须是对象。

---

## 三、统一返回结构
所有 runtime 调用统一返回一个 response 对象：

```json
{
  "ok": true,
  "runtimeMeta": {
    "action": "risk_check",
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "source": "skill_runtime_service",
    "requestId": "req-20260311T231400Z-ab12cd34",
    "traceId": "trace-20260311T231400Z-ef56gh78"
  },
  "data": {}
}
```

### 成功时
- `ok = true`
- `data` 中放业务结果

### 失败时
- `ok = false`
- 应返回 `error`
- 可返回 `message`
- 仍建议返回 `runtimeMeta`

错误示例：

```json
{
  "ok": false,
  "error": "UNSUPPORTED_ACTION",
  "message": "暂不支持的 runtime action: foo",
  "runtimeMeta": {
    "action": "foo",
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "source": "skill_runtime_service",
    "requestId": "req-20260311T231400Z-ab12cd34",
    "traceId": "trace-20260311T231400Z-ef56gh78"
  }
}
```

---

## 四、当前支持的 action
当前第一版支持：

1. `snapshot`
2. `risk_check`
3. `alert_to_risk`
4. `alert_to_review`
5. `risk_to_record`
6. `record_to_review`

---

## 五、各 action 输入输出契约

## 1. `snapshot`
### 作用
读取统一市场快照。

### request
```json
{
  "action": "snapshot",
  "payload": {
    "pair": "BTCUSDT"
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### payload 必填
- `pair`

### response.data
返回 `MarketSnapshot` 对象。

---

## 2. `risk_check`
### 作用
执行开仓前风险检查。

### request
```json
{
  "action": "risk_check",
  "payload": {
    "pair": "BTCUSDT",
    "side": "做空",
    "leverage": 10,
    "position_size": "未提供",
    "holding": "短线",
    "reason": "涨太多了，想吃一波回调"
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### payload 重点字段
- `pair` / `symbol`
- `side`
- `leverage`
- `positionSize` / `position_size`
- `stopLoss` / `stop_loss`
- `plannedHoldingTime` / `holding`
- `thesis` / `reason`

### response.data
返回当前 `run_risk_check(...)` 的输出结构：
- `mode`
- `plan`
- `marketSnapshot`
- `riskResult`
- `report`

---

## 3. `alert_to_risk`
### 作用
模拟新币提醒后，用户选择进入风控。

### request
```json
{
  "action": "alert_to_risk",
  "payload": {
    "event": {
      "symbol": "BTC",
      "pair": "BTCUSDT",
      "listingTime": "2026-03-11 18:00（UTC+8）"
    },
    "plan": {
      "pair": "BTCUSDT",
      "side": "做空",
      "leverage": 10,
      "position_size": "未提供",
      "holding": "短线",
      "reason": "涨太多了，想吃一波回调"
    }
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### payload 必填
- `event`
- `plan`

### response.data
返回：
- `listingEvent`
- `marketSnapshot`
- `alertMessage`
- `userAction`
- `riskCheck`

---

## 4. `alert_to_review`
### 作用
模拟新币提醒后，用户选择进入速评。

### request
```json
{
  "action": "alert_to_review",
  "payload": {
    "event": {
      "symbol": "BTC",
      "pair": "BTCUSDT",
      "listingTime": "2026-03-11 18:00（UTC+8）"
    }
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### payload 必填
- `event`

### response.data
返回：
- `listingEvent`
- `marketSnapshot`
- `alertMessage`
- `userAction`
- `quickReview`

---

## 5. `risk_to_record`
### 作用
执行风控后，记录这笔交易计划。

### request
```json
{
  "action": "risk_to_record",
  "payload": {
    "plan": {
      "pair": "BTCUSDT",
      "side": "做空",
      "leverage": 10,
      "position_size": "未提供",
      "holding": "短线",
      "reason": "涨太多了，想吃一波回调"
    }
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### userId 来源规则
优先顺序：
1. `context.userId`
2. `payload.userId`
3. fallback：`unknown-user`

### response.data
返回：
- `riskCheck`
- `userAction`
- `tradeReviewRecord`

---

## 6. `record_to_review`
### 作用
读取最近记录并生成轻量复盘。

### request
```json
{
  "action": "record_to_review",
  "payload": {
    "result": "loss",
    "reviewNote": "这单最后止损了。"
  },
  "context": {
    "channel": "telegram",
    "userId": "telegram:6482140148",
    "requestId": "req-...",
    "traceId": "trace-..."
  }
}
```

### payload 可选字段
- `result`
- `reviewNote`

### response.data
返回：
- `userAction`
- `tradeReviewRecord`
- `reviewOutput`

---

## 六、推荐 context 字段
当前建议 context 至少支持：

- `channel`
- `userId`
- `source`
- `requestId`
- `traceId`

示例：

```json
{
  "channel": "telegram",
  "userId": "telegram:6482140148",
  "source": "openclaw_skill_runtime",
  "requestId": "req-20260311T231400Z-ab12cd34",
  "traceId": "trace-20260311T231400Z-ef56gh78"
}
```

### 当前用途
- 标记请求来源
- 给 runtime 返回 `runtimeMeta`
- 给记录 / 复盘链提供 userId 线索
- 提供最小调用追踪标识

---

## 七、错误表达建议
当前第一版建议统一使用：

- `ok = false`
- `error = <ERROR_CODE>`
- `message = <human readable message>`
- `runtimeMeta`

### 当前已存在 / 可复用错误风格
- `UNSUPPORTED_ACTION`
- `INVALID_INPUT`
- `PAIR_NOT_FOUND`
- `UPSTREAM_TIMEOUT`
- `UPSTREAM_ERROR`
- `PARSE_ERROR`
- `UNKNOWN_ERROR`
- `NO_RECORD_FOUND`

注意：
当前 runtime service 已开始保留下层部分错误码，
但还没有形成完整的全链路错误分层与观测体系。

---

## 八、当前契约的边界
这份契约当前只定义：
- 最小 action 集
- 最小 request / response envelope
- MVP 第一版核心动作的 payload 结构
- 最小 requestId / traceId 追踪字段

它还没有定义：
- HTTP 路由
- 鉴权机制
- 幂等键
- span 级 trace
- 回调 / 异步任务格式
- 多版本兼容规则

所以这份契约的目标是：

> **先把 MVP 第一版 runtime 入口说清楚，再逐步加复杂度。**

---

## 九、当前阶段一句话结论
当前最合适的做法不是继续把入口逻辑散落在 CLI 或单个脚本里，
而是：

> **用统一的 `action + payload + context -> ok + runtimeMeta + data` 结构，作为新币合约交易冷静器 2.1 的第一版 Skill runtime 输入输出契约，并开始补上最小 requestId / traceId 追踪能力。**

这会是后续正式 Skill 接入、API 封装、调度接入、状态回写与调用追踪的共同基础。
