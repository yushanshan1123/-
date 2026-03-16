# DELIVERY_STATUS_QUERY_MOCK_NOTES.md

## 当前新增内容
已新增：
- `delivery_status_query_mock.py`
- `validate_delivery_status_query_mock.py`

## 这层的定位
这不是正式发送状态查询接口，
而是一个本地查询 mock。

它的作用是：
- 从 `delivery_status_records.json` 读取发送状态
- 提供最小查询方式
- 让发送状态不只会写，还能更像未来被查询

## 当前已支持的查询
### 1. `latest`
- 查看某个用户最近一条发送记录

### 2. `by_request_id`
- 按 `requestId` 查看一条发送记录

### 3. `list`
- 按用户列出最近若干条发送记录

## 当前边界
目前没有：
- 正式数据库查询
- 复杂过滤
- 权限边界
- 分页

所以它应被理解为：

> **发送状态可查询能力的本地 mock。**
