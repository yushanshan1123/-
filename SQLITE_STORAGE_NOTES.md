# SQLITE_STORAGE_NOTES.md

## 当前状态
`record_repository` 已默认切到 SQLite 实现：
- 数据库文件：`trade_review_records.sqlite3`
- 旧 JSON 文件：`trade_review_records.json`

## 当前迁移策略
为了避免直接打断已有原型数据，当前采用：

1. repository 首次访问时自动建表
2. 如果 SQLite 里还没有记录，则尝试从 `trade_review_records.json` 导入历史记录
3. 导入后新写入与新查询默认都走 SQLite

## 这意味着什么
- 业务层已经不再依赖 JSON 文件
- 存储默认实现已经不是 JSON，而是 SQLite
- 旧 JSON 当前保留为迁移来源与备份，不作为主存储

## 下一步建议
后续可以考虑：
- 增加一次性迁移脚本 / 校验脚本
- 增加 SQLite 查询测试
- 确认稳定后停止更新 JSON 文件，并在状态板中明确“JSON 仅为历史迁移来源”
