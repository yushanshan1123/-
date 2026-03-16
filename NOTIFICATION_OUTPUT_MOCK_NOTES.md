# NOTIFICATION_OUTPUT_MOCK_NOTES.md

## 当前新增内容
已新增：
- `notification_output_mock.py`
- `validate_notification_output_mock.py`

## 这层的定位
这不是正式消息发送器，
而是一个本地“输出适配”mock。

它的作用是：
- 接住 runtime 结果
- 按不同 userAction 渲染成更像可发送内容的结构
- 提前验证提醒链不只停在 runtime 结果，而是能继续走到“准备发送”的样子

## 当前已支持
### 1. 速评输出
- 标题：`【新币速评推送】`
- 内容：优先取 `quickReview`

### 2. 风控输出
- 标题：`【新币风控推送】`
- 内容：优先取 `riskCheck.report`

### 3. 失败输出
- 标题：`【提醒发送失败】`
- 内容：错误消息

## 当前边界
目前没有：
- 真正消息发送
- 渠道模板差异
- 富文本按钮
- 重试 / 送达状态

所以它应被理解为：

> **提醒发送前一层的本地输出适配样板。**
