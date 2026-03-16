# SCHEDULER_JOB_RUNNER_NOTES.md

## 当前新增内容
已新增：
- `scheduler_job_runner.py`
- `validate_scheduler_job_runner.py`

## 这层的定位
这是一层本地可运行的最小 scheduler runner。

它的作用是：
- 从 JSON 文件读取 jobs
- 逐个调用 `scheduler_runtime_entry_mock.py`
- 输出每个 job 的执行结果

## 当前价值
这意味着当前项目已经不只是“单个 scheduler mock 函数调用”，
而是有了一个：

> **可批量执行 job 的本地 scheduler runner。**

## 当前边界
目前仍然没有：
- 真正 cron 调度
- 去重
- 重试
- 失败队列
- job 状态持久化

所以它应被理解为：

> **从 scheduler entry mock 继续推进到最小本地 runner 的过渡层。**
