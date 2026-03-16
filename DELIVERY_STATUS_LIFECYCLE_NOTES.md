# DELIVERY_STATUS_LIFECYCLE_NOTES.md

## 当前新增内容
已新增/更新：
- `services/delivery_service/lifecycle.py`
- `validate_delivery_status_lifecycle.py`
- `repositories/delivery_status_repository/sqlite_repository.py`

## 这次变更的目标
这次不是上完整消息状态机，
而是先补最小状态流转骨架：

- `queued -> sent -> delivered`
- `queued -> failed`
- `sent -> failed`

## 当前价值
这意味着当前项目已经不只有：
- 发送结果留痕
- 状态查询

还开始有：
- 最小状态流转规则
- repository 级状态更新入口
- providerMessageId 随状态流转保留

## 当前边界
目前仍然没有：
- 自动重试
- 失败队列
- webhook / provider 回执接入
- 更复杂的多状态生命周期治理

所以它应被理解为：

> **真实发送状态机之前的最小 lifecycle 骨架。**
