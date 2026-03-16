# EXTERNAL_ENTRY_DEMO_NOTES.md

## 当前新增内容
已新增：
- `external_entry_demo.py`
- `validate_external_entry_demo.py`

## 这层的定位
这是一层统一 external entry 演示脚本。

它的作用是：
- 演示 HTTP 入口如何调 runtime
- 演示 scheduler 入口如何跑 job
- 演示通知整链如何从 scheduler 一路走到 delivery

## 当前支持模式
- `http-risk-check`
- `scheduler-review`
- `notification-review`
- `all`

## 当前价值
这意味着当前项目已经不只是有很多分散的入口样板，
而是有了一个：

> **统一演示外部入口如何调用整套后端骨架的入口脚本。**

## 当前边界
目前它仍然是 demo / orchestration 层，
不是正式部署入口，也不包含鉴权、监控、重试等生产能力。
