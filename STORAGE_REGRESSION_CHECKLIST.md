# STORAGE_REGRESSION_CHECKLIST.md

## 项目名称
新币合约交易冷静器 2.1

## 目标
这份清单用于明确：

> **当前 record_repository 默认切到 SQLite 后，最小需要确认哪些点。**

---

## 一、最小校验范围
当前最小必须确认的，不求大而全，只求关键链路别坏：

### repository 基础能力
- [x] `create_record(...)`
- [x] `get_record_by_id(...)`
- [x] `get_latest_record(...)`
- [x] `list_records(...)`
- [x] `update_record(...)`

### 存储落地
- [x] SQLite 文件可自动创建
- [x] SQLite 表可正常写入
- [x] 更新后数据可再次读出

### 闭环回归
- [x] `risk_to_record_prototype.py` 可继续写记录
- [x] `record_to_review_prototype.py` 可继续读取并复盘

---

## 二、当前已采用的校验方式
### 1. 闭环回归
已实际运行：
- `python3 risk_to_record_prototype.py`
- `python3 record_to_review_prototype.py`

用于确认：
- service → repository → SQLite 没坏
- 记录 / 复盘链仍可跑

### 2. repository 校验脚本
已新增：
- `validate_record_repository_sqlite.py`

用于确认：
- 基础 CRUD / list 能力可用
- SQLite 文件与记录确实存在

---

## 三、当前仍未覆盖的点
这份最小回归还没有覆盖：

- 并发写入
- 非法字段 / 异常 patch
- 更复杂的多条件查询
- 大量历史记录下的性能
- SQLite ↔ JSON 迁移一致性比对脚本

所以当前结论应保持诚实：

> **SQLite 默认存储已经可用，并完成了最小回归验证，但还没有达到完整测试覆盖。**
