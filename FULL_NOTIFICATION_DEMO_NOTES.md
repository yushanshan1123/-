# FULL_NOTIFICATION_DEMO_NOTES.md

## 当前新增内容
已新增：
- `full_notification_demo.py`
- `validate_full_notification_demo.py`

## 这层的定位
这不是正式生产链路，
而是一个一键整链演示脚本。

它的作用是：
- 从公告事件出发
- 经过 scheduler mock
- 进入 runtime / alert 分流
- 继续走到 notification output mock
- 最后走到 telegram output mock

## 当前支持模式
### 1. `review`
演示：
- 公告事件 → 速评链 → Telegram 输出样式

### 2. `risk`
演示：
- 公告事件 + 计划 → 风控链 → Telegram 输出样式

## 当前价值
这意味着现在可以用一条命令，直接演示：

> **公告事件如何一路变成更像 Telegram 最终发送载荷的结构。**

## 当前边界
目前没有：
- 真正消息发送
- 真正 scheduler
- 真正外部入口
- 真正状态回写

所以它应被理解为：

> **提醒链整链演示脚本，而不是正式生产流程。**
