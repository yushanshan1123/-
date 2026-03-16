# DELIVERY_STATUS_REGRESSION_CHECKLIST.md

## 项目名称
新币合约交易冷静器 2.1

## 目标
这份清单用于明确：

> **当前 delivery_status_repository 默认切到 SQLite 后，最小需要确认哪些点。**

---

## 一、最小校验范围
### repository 基础能力
- [x] `append_delivery_record(...)`
- [x] `get_latest_delivery_record(...)`
- [x] `get_delivery_record_by_request_id(...)`
- [x] `list_delivery_records(...)`

### 存储落地
- [x] SQLite 文件可自动创建
- [x] SQLite 表可正常写入
- [x] 按 `requestId` 可在 SQLite 中查到记录

### 发送链回归
- [x] `delivery_facade_mock.py` 可继续写发送状态
- [x] `delivery_status_query_mock.py` 可继续查询发送状态

---

## 二、当前已采用的校验方式
### 1. 发送状态查询回归
已实际运行：
- `python3 validate_delivery_status_query_mock.py`

### 2. SQLite 校验脚本
已新增：
- `validate_delivery_status_sqlite.py`

用于确认：
- SQLite 默认实现已接管
- repository 基础能力仍可用
- 记录确实落入 SQLite

---

## 三、当前仍未覆盖的点
这份最小回归还没有覆盖：
- 状态更新流转
- 并发写入
- 更复杂过滤 / 分页
- 真实发送结果映射

所以当前最准确的结论应是：

> **发送状态默认存储已经切到 SQLite，并完成了最小可运行校验，但还没有达到完整生产级消息状态测试覆盖。**
