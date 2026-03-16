# DELIVERY_STATUS_SQLITE_NOTES.md

## 当前状态
`delivery_status_repository` 已默认切到 SQLite 实现：
- 数据库文件：`delivery_status_records.sqlite3`
- 旧 JSON 文件：`delivery_status_records.json`

## 当前迁移策略
为了避免打断现有本地发送状态样板，当前采用：

1. repository 首次访问时自动建表
2. 如果 SQLite 里还没有记录，则尝试从 `delivery_status_records.json` 导入历史记录
3. 导入后新写入与新查询默认都走 SQLite

## 这意味着什么
- facade / query 层已不再依赖 JSON 文件
- 发送状态默认实现已经不是 JSON，而是 SQLite
- 旧 JSON 当前保留为迁移来源与备份，不作为主存储

## 当前边界
目前还没有：
- 独立迁移比对脚本
- 更完整的状态更新流转
- 更复杂的过滤和分页

所以它应被理解为：

> **发送状态存储默认实现从 JSON 推进到 SQLite 的第一步。**
