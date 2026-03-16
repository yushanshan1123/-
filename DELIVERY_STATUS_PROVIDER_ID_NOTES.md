# DELIVERY_STATUS_PROVIDER_ID_NOTES.md

## 当前新增内容
已新增/更新：
- `repositories/delivery_status_repository/sqlite_repository.py`
- `validate_delivery_status_sqlite.py`

## 这次变更的目标
这次不是重做发送状态层，
而是给当前 SQLite repository 补一个向前兼容字段：

- `providerMessageId`

## 为什么现在补
因为当前 delivery result schema 已经固定包含：
- `providerMessageId`
- `mockMessageId`

如果 repository 还只存 `mockMessageId`，
等真实发送一接入，就还要回头补 schema / migration / validation。

所以现在先把库层对齐，后面会顺很多。

## 当前价值
这意味着 delivery status SQLite 现在已经开始兼容两类结果：
- 当前 mock 结果
- 未来真实 provider 结果

## 当前边界
目前仍然没有：
- 更完整的消息状态生命周期
- delivered / failed 状态回写
- provider message id 的真实渠道接入

所以它应被理解为：

> **为未来真实发送结果预留 providerMessageId 的向前兼容升级。**
