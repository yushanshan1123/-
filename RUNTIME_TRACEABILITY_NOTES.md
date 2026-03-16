# RUNTIME_TRACEABILITY_NOTES.md

## 当前新增内容
adapter → runtime 这条链已开始支持：
- `requestId`
- `traceId`

## 当前策略
### 1. adapter 侧
- 若外部已传 `requestId` / `traceId`，则直接透传
- 若未传 `requestId`，则自动生成最小 requestId
- 若未传 `traceId`，则默认复用 `requestId`

### 2. runtime 侧
`runtimeMeta` 现在已返回：
- `action`
- `channel`
- `userId`
- `source`
- `requestId`
- `traceId`

## 当前价值
这意味着从 adapter 到 runtime 的一次调用，
已经开始具备最小可追踪标识。

## 当前边界
目前仍然没有：
- 全链路日志系统
- 正式 trace 平台
- span 级追踪
- 请求持久化审计

所以它现在应被理解为：

> **最小调用追踪骨架，而不是完整 observability 系统。**
