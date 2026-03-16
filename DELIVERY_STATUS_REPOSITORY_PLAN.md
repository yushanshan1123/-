# DELIVERY_STATUS_REPOSITORY_PLAN.md

## 当前新增内容
已新增：
- `repositories/delivery_status_repository/`

## 这层的定位
这不是正式消息状态数据库层，
但它已经把发送状态从“脚本直接写文件”往“repository 边界”推进了一步。

## 当前做了什么
- 把 `delivery_status_records.json` 的读写收进 repository
- 把 append / latest / by_request_id / list 都放进统一存取边界
- 让 facade 与 query mock 都不再直接碰底层文件

## 当前价值
这意味着发送状态这块已经开始形成：
- facade / query 层
- repository 层
- 本地 JSON 存储实现

## 当前边界
目前仍然没有：
- SQLite / 正式数据库实现
- 更完整的过滤与分页
- 权限治理

所以它应被理解为：

> **发送状态存储边界的第一版正式化。**
