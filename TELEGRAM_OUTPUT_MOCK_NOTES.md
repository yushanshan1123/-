# TELEGRAM_OUTPUT_MOCK_NOTES.md

## 当前新增内容
已新增：
- `telegram_output_mock.py`
- `validate_telegram_output_mock.py`

## 这层的定位
这不是正式 Telegram 发送器，
而是一个本地 Telegram 输出渲染 mock。

它的作用是：
- 接住通用 `notificationOutput`
- 再转成更像 Telegram 最终发送载荷的结构
- 提前验证提醒链可以继续从“输出适配”走到“渠道输出样式”

## 当前已支持
### 1. 速评 Telegram 输出
- 正文 = 标题 + 内容
- 附带按钮：查看风控 / 忽略

### 2. 风控 Telegram 输出
- 正文 = 标题 + 内容
- 附带按钮：记录这笔计划 / 忽略

## 当前边界
目前没有：
- 真正 message tool 发送
- 真正 Telegram callback handler
- 真正按钮回调状态管理

所以它应被理解为：

> **提醒输出进一步贴近 Telegram 渠道样式的本地 mock。**
