# LISTING_EVENT_SCHEDULER_DEMO_NOTES.md

## 当前新增内容
已新增：
- `listing_event_scheduler_review_demo.py`
- `listing_event_scheduler_risk_demo.py`

## 这层的定位
这两个脚本不是正式公告调度系统，
而是本地演示：

> **公告事件如何先进入 scheduler mock，再进入 runtime / alert 分流链，并继续走到输出适配层。**

## 当前演示的两条链
### 1. 公告事件 → scheduler → alert_to_review → output mock
适合演示：
- 调度触发速评分流
- 事件如何被整理成 scheduler job
- scheduler job 如何进入 adapter / runtime
- runtime 结果如何继续转换成更像可发送内容的输出结构

### 2. 公告事件 → scheduler → alert_to_risk → output mock
适合演示：
- 调度触发提醒后，直接进入风控分流
- 事件 + 计划如何一起进入 runtime 链
- 风控结果如何继续转换成更像可发送内容的输出结构

## 当前价值
这一步的价值不是“真实调度已经完成”，
而是：
- 提醒调度链开始有本地可跑样板
- 公告事件不再只停在文档或 prototype 入口
- scheduler 入口、alert 分流、输出适配之间已有可演示桥接

## 当前边界
目前没有：
- 真正公告监控
- 真正任务调度器
- 真正消息发送
- 真正状态回写

所以它应被理解为：

> **提醒真实调度链路到输出适配层的本地演示样板，而不是正式调度实现。**
