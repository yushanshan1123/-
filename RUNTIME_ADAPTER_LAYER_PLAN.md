# RUNTIME_ADAPTER_LAYER_PLAN.md

## 项目名称
新币合约交易冷静器 2.1

## 目标
这份文档用于定义：

> **为什么在 `skill_runtime_service` 之上，再补一层 `runtime_adapter_service`。**

---

## 一、这层解决什么问题
当前 `skill_runtime_service` 已经负责：
- action 分发
- payload / context 校验
- 错误包装
- 一部分下层错误归一

但如果后面有不同入口同时接进来，例如：
- Telegram
- 未来 HTTP API
- 未来调度器
- 其他调用来源

那么它们仍然需要一个地方统一做：
- 外部入口参数整理
- 外部身份 / channel → runtime context 映射
- 请求组装
- 未来 trace / request id 注入

这就是 `runtime_adapter_service` 的位置。

---

## 二、推荐分层关系
推荐理解成：

外部入口（Telegram / HTTP / Scheduler / 其他）
↓
`runtime_adapter_service`
↓
`skill_runtime_service`
↓
`skill_entry_service`
↓
业务 service / repository

---

## 三、当前第一版做了什么
当前已新增：
- `services/runtime_adapter_service/service.py`

第一版先不做复杂逻辑，
只做两件事：

### 1. `adapt_external_call(...)`
把外部调用统一组装成 runtime request：
- `action`
- `payload`
- `context`

### 2. `adapt_telegram_runtime_call(...)`
把 Telegram 场景下常见的：
- `channel`
- `userId`
- `source`
- `requestId`

先统一装进 context。

---

## 四、这层当前的价值
这层的价值不是“功能变多”，
而是：

> **让未来外部入口不必直接碰 `skill_runtime_service` 的细节。**

也就是说，后面如果要接：
- HTTP handler
- webhook
- 调度器
- 消息入口

更自然的接法会是：

> 先走 adapter，再进 runtime。

---

## 五、当前边界
当前这层还没有做：
- 正式 HTTP 路由
- 鉴权
- trace id 统一生成
- 签名校验
- 限流
- 请求审计

所以它现在应被理解为：

> **外部调用适配层骨架，而不是正式 API 网关。**
