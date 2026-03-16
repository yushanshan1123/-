# HTTP_ENTRY_MOCK_NOTES.md

## 当前新增内容
已新增：
- `http_runtime_entry_mock.py`
- `validate_http_runtime_entry_mock.py`

## 这层的定位
这不是正式 HTTP API，
而是一个本地可跑的最小入口伪实现。

它的作用是：
- 模拟未来 HTTP handler
- 把 body / headers 映射成 adapter 调用
- 提前验证 HTTP → adapter → runtime 这条链的接法

## 当前已模拟的映射
### body
- `action`
- `payload`
- `userId`

### headers
- `X-Request-Id`
- `X-Trace-Id`

### context
映射后统一进入：
- `channel = http`
- `source = runtime_adapter_service.http`
- `requestId`
- `traceId`

## 当前边界
目前没有：
- 真正 HTTP server
- 路由
- 鉴权
- 限流
- 状态码映射策略

所以它应被理解为：

> **未来 HTTP 入口接 adapter 的本地模拟样板。**
