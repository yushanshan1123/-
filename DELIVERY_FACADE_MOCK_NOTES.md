# DELIVERY_FACADE_MOCK_NOTES.md

## 当前新增内容
已新增：
- `delivery_facade_mock.py`
- `validate_delivery_facade_mock.py`

## 这层的定位
这不是正式渠道发送器，
而是一个发送接口占位 facade。

它的作用是：
- 接住渠道输出 payload
- 模拟“准备发送 / 已发送”结果
- 让提醒链继续从 Telegram 输出样式再往“发送接口结果”靠一步

## 当前已支持
- 输入任意渠道 payload
- 输出统一的 mock delivery result
- 返回：
  - `deliveryStatus`
  - `deliveryChannel`
  - `targetUserId`
  - `mockMessageId`
  - `sentAt`
  - `requestId`
  - `traceId`

## 当前边界
目前没有：
- 真正 message.send 调用
- 真正送达结果
- 真正失败重试
- 真正渠道差异处理

所以它应被理解为：

> **真实发送接口前一层的本地占位 facade。**
