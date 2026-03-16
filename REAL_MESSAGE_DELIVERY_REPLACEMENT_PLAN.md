# REAL_MESSAGE_DELIVERY_REPLACEMENT_PLAN.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **如何把当前提醒链里的本地发送 mock / facade，逐步替换成真实消息发送接口。**

当前提醒链已经能演示到：
- 公告事件
- scheduler mock
- adapter
- runtime
- alert 分流
- notification output mock
- telegram output mock
- delivery facade mock

这意味着：

> **提醒链的“发送前”与“发送占位结果”已经有了工程结构。**

下一步要解决的问题，不再是“消息该不该发”，
而是：

- 哪一层以后替换成真实发送？
- 哪些层应该保留？
- 哪些字段必须一直保留，方便状态回写与排查？

---

## 一、当前链路现状
当前本地演示链已经大致是：

公告事件
→ scheduler mock
→ adapter
→ runtime
→ alert 分流
→ notification output mock
→ telegram output mock
→ delivery facade mock

其中：

### 应长期保留的层
- `alert_service`
- `skill_entry_service`
- `skill_runtime_service`
- `runtime_adapter_service`

### 当前主要是本地样板 / 占位的层
- `notification_output_mock.py`
- `telegram_output_mock.py`
- `delivery_facade_mock.py`

也就是说，后续真正需要替换的，主要不是业务判断层，
而是：

> **输出适配层与发送接口层。**

---

## 二、推荐替换原则
### 原则 1：业务层不要碰发送器细节
风控、速评、提醒分流逻辑，不应直接调用真实渠道发送接口。

### 原则 2：保留“输出适配”和“发送接口”两层分离
建议长期保留两层：

#### 1. 输出适配层
负责：
- 把 runtime 结果转成渠道无关的通知结构
- 再转成渠道相关 payload（如 Telegram 样式）

#### 2. 发送接口层
负责：
- 真正调用渠道发送接口
- 接住发送结果
- 统一回传送达状态 / messageId / 时间

### 原则 3：替换时优先替换 facade，而不是重写前面所有层
也就是说，未来最优先替换的是：

- `delivery_facade_mock.py`

而不是推倒重做整个提醒链。

---

## 三、推荐的正式替换方向
### 当前 mock 结构
#### `notification_output_mock.py`
作用：runtime 结果 → 通用通知输出

#### `telegram_output_mock.py`
作用：通用通知输出 → Telegram 风格 payload

#### `delivery_facade_mock.py`
作用：渠道 payload → mock delivery result

### 未来推荐方向
#### 1. 保留 `notification_output_mock.py` 的职责，但改名/正式化
未来可以正式化为类似：
- `notification_output_service`

#### 2. 保留 `telegram_output_mock.py` 的职责，但改名/正式化
未来可以正式化为类似：
- `telegram_delivery_adapter`

#### 3. 把 `delivery_facade_mock.py` 替换成真实发送 facade
未来可以正式化为类似：
- `delivery_facade`
- 或 `message_delivery_service`

其内部再决定是否调用：
- OpenClaw `message.send`
- 其他渠道 SDK
- 其他发送桥接层

---

## 四、最重要的保留字段
无论以后怎么替换，以下字段建议始终保留并贯穿：

### 1. `requestId`
用于定位这次调用。

### 2. `traceId`
用于把同一条链串起来。

### 3. `targetUserId`
用于确认目标是谁。

### 4. `deliveryChannel`
用于确认走的是哪个渠道。

### 5. `messageId` / `providerMessageId`
未来真实发送后应记录真实消息 ID。

### 6. `deliveryStatus`
建议统一保留，例如：
- `queued`
- `sent`
- `delivered`
- `failed`
- `mock_sent`

### 7. `sentAt`
记录发送时间。

这些字段很重要，因为后面如果要做：
- 状态回写
- 失败重试
- 发送排查
- 用户反馈定位

都会用到。

---

## 五、未来真实发送接口的最小返回建议
当前 mock 返回：
- `ok`
- `deliveryStatus`
- `deliveryChannel`
- `targetUserId`
- `mockMessageId`
- `sentAt`
- `requestId`
- `traceId`

未来替换成真实发送后，建议最小返回结构仍尽量长这样：

```json
{
  "ok": true,
  "deliveryStatus": "sent",
  "deliveryChannel": "telegram",
  "targetUserId": "telegram:6482140148",
  "providerMessageId": "123456",
  "sentAt": "2026-03-12T00:00:00Z",
  "requestId": "req-...",
  "traceId": "trace-..."
}
```

这样替换时，前后结构差异最小。

---

## 六、推荐替换顺序
建议按这个顺序推进：

### Step 1
继续保留：
- `notification_output_mock.py`
- `telegram_output_mock.py`

先把它们视为“接口已稳定、名字以后可调整”的过渡层。

### Step 2
把 `delivery_facade_mock.py` 替换成正式 `delivery_facade`
内部调用真实发送工具或消息桥接接口。

### Step 3
补最小发送状态记录能力。
至少记住：
- 发给谁
- 哪个渠道
- 发送时间
- 真实消息 ID（如果能拿到）
- requestId / traceId

### Step 4
再考虑：
- 失败重试
- 送达状态更新
- 更完整的渠道差异适配

---

## 七、当前不建议立刻做什么
为了避免一下子把工程做重，当前阶段不建议马上：

- 一次性接很多渠道
- 一次性做复杂消息模板引擎
- 一次性做完整消息状态机
- 一次性做完整失败队列 / 补偿系统

当前最重要的是：

> **先把“真实发送替换点”钉死在 facade 层。**

---

## 八、当前阶段一句话结论
当前最正确的推进方式不是重写整条提醒链，
而是：

> **保留现有业务层、runtime 层、adapter 层和输出适配层，优先把 `delivery_facade_mock.py` 这个占位点，未来替换成真实消息发送接口。**

这会是新币合约交易冷静器 2.1 从“本地提醒演示链”走向“真实可发提醒链”的最自然一步。
