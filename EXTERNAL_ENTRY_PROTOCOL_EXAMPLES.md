# EXTERNAL_ENTRY_PROTOCOL_EXAMPLES.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **未来不同外部入口，应该如何映射成 `runtime_adapter_service` 调用。**

这份文档的重点不是去定义真正的 HTTP API 或机器人框架细节，
而是先回答一个更实际的问题：

- Telegram 消息进来后，怎么转成 adapter 调用？
- 未来 HTTP 请求进来后，怎么转成 adapter 调用？
- 未来调度器触发后，怎么转成 adapter 调用？

也就是说，这是一份：

> **外部入口 → adapter 层 的示例协议文档。**

---

## 一、推荐总体关系
推荐统一理解成：

外部入口
↓
入口处理器（Telegram handler / HTTP handler / Scheduler handler）
↓
`runtime_adapter_service`
↓
`skill_runtime_service`
↓
`skill_entry_service`
↓
业务 service / repository

这里的关键原则是：

> **外部入口不直接碰业务 service，也尽量不直接碰 runtime 内部细节。**

---

## 二、Telegram 入口示例
### 适用场景
- 用户在 Telegram 里触发某个动作
- 例如点按钮、发关键词、回复特定命令

### 推荐映射方式
Telegram handler 负责：
- 识别用户意图对应的 `action`
- 整理 `payload`
- 提取 `userId`
- 生成 / 透传 `requestId`
- 调 `adapt_telegram_runtime_call(...)`

### 示例：用户想做风控
伪代码：

```python
result = adapt_telegram_runtime_call(
    action='risk_check',
    payload={
        'pair': 'BTCUSDT',
        'side': '做空',
        'leverage': 10,
        'position_size': '未提供',
        'holding': '短线',
        'reason': '涨太多了，想吃一波回调',
    },
    user_id='telegram:6482140148',
    request_id='tg-msg-12345',
    trace_id='trace-tg-12345',
)
```

### Telegram handler 应负责什么
- 把 Telegram 特有字段映射到：
  - `userId`
  - `requestId`
  - `traceId`
- 决定要走哪个 `action`
- 决定返回结果如何再发回 Telegram

### Telegram handler 不应负责什么
- 不直接写风控逻辑
- 不直接拼市场快照
- 不直接写记录文件

---

## 三、HTTP 入口示例
### 适用场景
- 后续如果要暴露一个轻量内部 API
- 例如内部后端或 webhook 调用

### 推荐映射方式
HTTP handler 负责：
- 从 HTTP body 读取 `action` / `payload`
- 从 header 或中间件里拿 `requestId` / `traceId`
- 组装 `context`
- 调 `adapt_external_call(...)`

### 示例
伪代码：

```python
result = adapt_external_call(
    action=body['action'],
    payload=body.get('payload', {}),
    context={
        'channel': 'http',
        'userId': body.get('userId'),
        'source': 'runtime_adapter_service.http',
        'requestId': request.headers.get('X-Request-Id'),
        'traceId': request.headers.get('X-Trace-Id'),
    },
)
```

### 推荐的最小 HTTP body 形状
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
  "userId": "telegram:6482140148"
}
```

### HTTP handler 应负责什么
- 请求体解析
- 鉴权（未来）
- header → context 映射
- HTTP status code 与 runtime response 的转换

### HTTP handler 不应负责什么
- 不直接调用 `risk_check_service`
- 不直接构造复盘输出
- 不直接处理下游数据库细节

---

## 四、调度器 / 定时任务入口示例
### 适用场景
- 后续做公告轮询
- 上线前提醒
- 定时状态检查

### 推荐映射方式
Scheduler handler 负责：
- 产生 `action`
- 整理事件 `payload`
- 标记 `source = scheduler`
- 调 `adapt_external_call(...)`

### 示例：定时触发“提醒 → 速评”
伪代码：

```python
result = adapt_external_call(
    action='alert_to_review',
    payload={
        'event': {
            'symbol': 'BTC',
            'pair': 'BTCUSDT',
            'listingTime': '2026-03-11 18:00（UTC+8）'
        }
    },
    context={
        'channel': 'scheduler',
        'source': 'runtime_adapter_service.scheduler',
        'requestId': 'sched-job-001',
        'traceId': 'trace-sched-001',
    },
)
```

### Scheduler handler 应负责什么
- 时间触发
- 任务去重（未来）
- 调度上下文注入

### Scheduler handler 不应负责什么
- 不自己拼提醒文案逻辑
- 不自己做风控判断
- 不自己处理记录写入逻辑

---

## 五、未来推荐的入口最小规范
无论是 Telegram / HTTP / Scheduler，建议都尽量统一成：

### 入口处理器负责
- 识别来源
- 提取身份
- 注入 `requestId`
- 注入 `traceId`
- 组装 `action`
- 组装 `payload`
- 调 adapter

### adapter 负责
- 统一组装 runtime request
- 补默认 context
- 保持外部入口与 runtime 解耦

### runtime 负责
- 输入校验
- 错误包装
- 错误归一
- 调下层入口/service

---

## 六、当前边界
这份文档当前只是“示例协议”，
还没有真正定义：
- Telegram Bot 框架代码
- HTTP 路由定义
- Webhook 安全策略
- Scheduler 去重机制
- 权限系统

所以它当前最准确的定位是：

> **为未来正式外部入口落地提供统一接法样板。**

---

## 七、当前阶段一句话结论
当前最稳的做法不是让每个外部入口自己直接碰 runtime 内部细节，
而是：

> **统一让 Telegram / HTTP / Scheduler 等入口先映射到 `runtime_adapter_service`，再进入 `skill_runtime_service`。**

这样后续新币合约交易冷静器 2.1 才更容易从“内部工程骨架”走向“真正可被外部入口稳定调用的 MVP”。
