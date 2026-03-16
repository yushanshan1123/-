# SKILL_RUNTIME_VALIDATION_NOTES.md

## 当前新增能力
`skill_runtime_service` 已新增两类能力：

### 1. 输入校验
当前已校验：
- request 必须是对象
- `action` 必须存在且为非空字符串
- `payload` / `context` 若存在必须是对象
- 各 action 的必填字段是否存在
- `event` / `plan` 等嵌套对象是否为对象
- `risk_check.side` / `plan.side` 是否在支持范围内
- `alert_to_review` / `alert_to_risk` 的 `event.symbol`、`event.pair` 是否有效
- `record_to_review.result` 是否在支持范围内
- `pair` / `symbol` 是否符合最小格式规则
- `leverage` 是否为正数且不超过合理上限
- `listingTime` 不能为空字符串且长度不过长
- `reviewNote` 长度不能超过上限

### 2. 错误包装 / 归一化
当前已统一包装：
- `INVALID_INPUT`
- `UNSUPPORTED_ACTION`
- `UNKNOWN_ERROR`

当前已尽量透传 / 归一：
- `NO_RECORD_FOUND`
- `INVALID_INPUT`
- `PAIR_NOT_FOUND`
- `UPSTREAM_TIMEOUT`
- `UPSTREAM_ERROR`
- `UPSTREAM_PARTIAL_ERROR`
- `PARSE_ERROR`

并统一输出：
- `ok = false`
- `error`
- `message`
- `runtimeMeta`
- 可选 `details`

## 当前价值
这意味着 runtime 层已经不只是“把请求转发下去”，
而是开始承担：
- 入口层基本防呆
- 错误格式统一
- action 级输入边界约束
- 一部分业务关键字段的最小值域校验
- 一部分常见格式错误和明显坏值的前置拦截
- 下层常见错误码的保留与归一

## 当前边界
目前还没有做：
- 更细粒度的业务策略校验（如不同场景的 leverage 建议阈值）
- 更完整的上游异常分类（如网络错误细分）
- trace id / request id
- 幂等与重试策略
