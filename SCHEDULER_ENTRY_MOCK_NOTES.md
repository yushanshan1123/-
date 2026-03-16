# SCHEDULER_ENTRY_MOCK_NOTES.md

## 当前新增内容
已新增：
- `scheduler_runtime_entry_mock.py`
- `validate_scheduler_runtime_entry_mock.py`

## 这层的定位
这不是正式调度系统，
而是一个本地可跑的 Scheduler / 定时任务入口 mock。

它的作用是：
- 模拟未来 scheduler handler
- 把 job payload 映射成 adapter 调用
- 提前验证 Scheduler → adapter → runtime 这条链的接法

## 当前已模拟的映射
### job 输入
- `jobName`
- `action`
- `payload`
- `userId`
- `requestId`
- `traceId`
- `source`

### context
映射后统一进入：
- `channel = scheduler`
- `source = runtime_adapter_service.scheduler`（可覆盖）
- `requestId`
- `traceId`
- `jobName`

## 当前边界
目前没有：
- 真正的 scheduler runner
- 去重
- 重试
- 失败队列
- cron 管理

所以它应被理解为：

> **未来 Scheduler 入口接 adapter 的本地模拟样板。**
