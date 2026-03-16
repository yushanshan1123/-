# MESSAGE_DELIVERY_RESULT_SCHEMA.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于固定：

> **发送接口层返回结果的最小统一结构。**

目标是避免未来从 mock 发送切到真实发送时，出现：
- 返回字段名来回变化
- delivery status 口径不一致
- repository 无法稳定存储
- 上层 demo / query / 排障代码频繁跟着改

---

## 一、最小返回结构
建议发送接口层统一返回：

```json
{
  "ok": true,
  "deliveryStatus": "sent",
  "deliveryChannel": "telegram",
  "targetUserId": "telegram:6482140148",
  "providerMessageId": "123456",
  "mockMessageId": null,
  "sentAt": "2026-03-12T00:00:00Z",
  "requestId": "req-...",
  "traceId": "trace-...",
  "payload": {}
}
```

---

## 二、字段说明
### `ok`
- 类型：`bool`
- 作用：这次发送调用本身是否成功返回

### `deliveryStatus`
- 类型：`str`
- 建议值：
  - `queued`
  - `sent`
  - `delivered`
  - `failed`
  - `mock_sent`

### `deliveryChannel`
- 类型：`str`
- 例如：`telegram`

### `targetUserId`
- 类型：`str | null`
- 例如：`telegram:6482140148`

### `providerMessageId`
- 类型：`str | null`
- 真实发送后记录 provider 返回的 message id

### `mockMessageId`
- 类型：`str | null`
- 当前 mock 实现保留该字段，未来可以为空

### `sentAt`
- 类型：`str`
- UTC ISO8601 时间

### `requestId`
- 类型：`str | null`
- 用于定位本次请求

### `traceId`
- 类型：`str | null`
- 用于串联整条调用链

### `payload`
- 类型：`object | null`
- 保留原始渠道 payload，便于排障与状态留痕

---

## 三、兼容策略
### 当前 mock 阶段
允许：
- `mockMessageId` 有值
- `providerMessageId` 为空
- `deliveryStatus = mock_sent`

### 未来真实发送阶段
建议：
- `providerMessageId` 有值
- `mockMessageId` 为空
- `deliveryStatus` 进入 `sent` / `delivered` / `failed`

---

## 四、与 repository 的关系
当前 `delivery_status_repository` 已默认落 SQLite。

未来如果要完全对齐真实发送结果，repository 建议逐步支持：
- `providerMessageId`
- 更完整的 `deliveryStatus` 生命周期

当前阶段则先保持：
- 结构尽量稳定
- mock / real 两种返回尽量同构

---

## 五、当前一句话结论

> **发送接口层未来无论走 mock 还是真发送，都应尽量返回同一套 delivery result 结构。**
