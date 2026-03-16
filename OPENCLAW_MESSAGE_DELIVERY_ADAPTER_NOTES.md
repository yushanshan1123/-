# OPENCLAW_MESSAGE_DELIVERY_ADAPTER_NOTES.md

## 当前新增内容
已新增/更新：
- `openclaw_message_delivery_adapter.py`
- `validate_openclaw_message_delivery_adapter.py`

## 这层的定位
这是一层真实发送适配器插槽。

它的作用是：
- 给 `delivery_facade.py` 提供未来真实发送的正式挂载点
- 当前在未接入 `message.send` 时，返回可识别的未配置结果
- 未来真实发送替换时，只改 adapter 内部实现

## 这次进一步补了什么
这次不只是保留一个空插槽，
而是已经补了三类 helper：
- payload -> `message.send` request 映射
- tool result -> delivery result 映射
- adapter error -> 标准 delivery result 映射

同时，facade 层也已经明确：
- 默认 mock
- 显式开关后先走 real adapter
- `NOT_CONFIGURED` 时允许 fallback 到 mock

## 当前价值
这意味着发送链现在已经不只是：
- formal facade
- real adapter slot
- mock fallback

而是开始具备：
- formal facade
- 可接 `message.send` 的 adapter 壳
- 明确的 real/mock 决策策略
- mock fallback

## 当前边界
目前它仍然没有真正调用 `message.send`。
所以它应被理解为：

> **真实发送接入前、映射壳和 facade 决策策略都已补齐的 adapter 插槽层。**
