# COINGLASS_FUNDING_API_CONTRACT.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于固定 **Coinglass Funding Connector** 的最小接口契约，避免后续开发时出现：

- Funding 字段定义不一致
- 拥挤方向（bias）口径反复变化
- 错误状态与 Binance 层不统一
- Skill 层不知道什么时候可以使用 Funding 判断

核心目标是：

> **让 Funding 这一层，成为一个可预测、可映射、可降级的增强数据接口。**

---

## 一、Connector 定位
Coinglass Funding Connector 的职责只有一个：

> **给一个交易对，返回当前资金费率及其最小拥挤度判断。**

它负责：
- 拉取 Funding 原始值
- 标准化数值
- 派生 `fundingBias`
- 返回状态

它不负责：
- 风控结论
- 提醒文案
- 复盘分析
- 用户交互

这些由后续业务层和 Skill 层完成。

---

## 二、最小接口名称建议
建议统一使用：

## `getCoinglassFunding(pair)`

如果系统侧已抽象成统一市场快照增强层，也可以由上层包装成：

## `getMarketSnapshot(pair)` 的 Funding 子层

但在 Connector 这一层，建议先保留明确语义：

> **这是 Funding Connector，不是通用市场接口。**

---

## 三、输入契约

### 最小输入
```json
{
  "pair": "LOBSTERUSDT"
}
```

### 字段说明
#### `pair`
- 类型：string
- 必填：是
- 含义：目标交易对
- 示例：`BTCUSDT` / `LOBSTERUSDT`

### 输入规则
- 必须是标准字符串
- 默认使用大写交易对
- 不能为空
- 与 Binance 主骨架保持同一套交易对口径

### 输入非法时的行为
如果 `pair` 缺失、为空或格式非法：
- 不调用远端数据源
- 直接返回错误状态

---

## 四、成功输出契约

### 标准成功输出
```json
{
  "pair": "LOBSTERUSDT",
  "fundingRate": 0.0001,
  "fundingBias": "long_crowded",
  "timestamp": "2026-03-11T17:20:00Z",
  "status": "ok"
}
```

### 字段定义
#### `pair`
- 类型：string
- 含义：返回结果对应的交易对

#### `fundingRate`
- 类型：number | null
- 含义：当前资金费率原始数值

#### `fundingBias`
- 类型：string | null
- 含义：基于 Funding 派生出的最小拥挤度判断
- 建议值：
  - `long_crowded`
  - `short_crowded`
  - `neutral`

#### `timestamp`
- 类型：string
- 含义：该结果生成时间
- 格式：ISO 8601 UTC

#### `status`
- 类型：string
- 枚举值：
  - `ok`
  - `partial`
  - `error`

---

## 五、`fundingBias` 定义规则
Funding 这一层最容易混乱的地方，就是 bias 口径不统一。

因此建议固定如下：

### 1. `long_crowded`
表示：
- 当前多头情绪偏拥挤
- 继续追多风险上升

### 2. `short_crowded`
表示：
- 当前空头情绪偏拥挤
- 继续追空风险上升

### 3. `neutral`
表示：
- 当前 Funding 没有明显极端倾向
- 不能靠 Funding 单独下判断

### 原则
`fundingBias` 是：
- 对原始 Funding 的辅助解释层
- 不是单点交易信号

Skill 不应把 `fundingBias` 直接当成买卖按钮。

---

## 六、状态定义

## 1. `ok`
表示：
- Connector 已成功获取 Funding 原始值
- 且已成功派生 `fundingBias`

### 判定条件
以下字段应存在且可用：
- `fundingRate`
- `fundingBias`
- `timestamp`

---

## 2. `partial`
表示：
- Connector 只获取到了部分 Funding 层信息
- 可作为有限参考，但不足以支持完整拥挤判断

### 典型情况
- 有 `fundingRate`
- 但 `fundingBias` 计算失败或暂不可判定

### 原则
- 已拿到的字段可以返回
- 未拿到的字段必须为 `null`
- 不能伪装成 `ok`

---

## 3. `error`
表示：
- Connector 无法提供可用 Funding 结果
- 不应作为当前风控依据

### 典型情况
- 输入非法
- Coinglass 请求失败
- 上游超时
- 原始值解析失败

### 原则
- 不返回伪造值
- 允许附带错误说明字段

---

## 七、错误输出契约

### 建议错误输出
```json
{
  "pair": "LOBSTERUSDT",
  "fundingRate": null,
  "fundingBias": null,
  "timestamp": "2026-03-11T17:21:00Z",
  "status": "error",
  "errorCode": "UPSTREAM_ERROR",
  "errorMessage": "Funding data unavailable from Coinglass"
}
```

### 扩展错误字段
#### `errorCode`
- 类型：string
- 可选：是
- 建议值：
  - `INVALID_INPUT`
  - `PAIR_NOT_FOUND`
  - `UPSTREAM_TIMEOUT`
  - `UPSTREAM_ERROR`
  - `PARSE_ERROR`
  - `UNKNOWN_ERROR`

#### `errorMessage`
- 类型：string
- 可选：是
- 含义：给开发和日志看的错误说明

---

## 八、字段级规则

## 1. 数值字段统一规则
#### `fundingRate`
必须统一为：
- `number`
- 或 `null`

### 不允许
- 百分号字符串
- 原始文本直接透传
- 带单位文本

例如：
允许：
- `0.0001`

不允许：
- `"0.01%"`
- `"0.0001"`

---

## 2. 时间字段规则
#### `timestamp`
必须：
- 使用 UTC
- 使用 ISO 8601 格式

例如：
- `2026-03-11T17:20:00Z`

---

## 3. 空值规则
如果字段拿不到：
- 必须明确返回 `null`
- 不允许省略关键字段

特别是：
- `fundingRate`
- `fundingBias`

---

## 九、与 `MarketSnapshot` 的映射契约
Funding Connector 输出不是最终给 Skill 的对象。
后端应将其映射进统一 `MarketSnapshot`。

### 映射示例
```json
{
  "fundingRate": 0.0001,
  "fundingBias": "long_crowded",
  "sourceCoinglassStatus": "ok"
}
```

### 映射规则
- `fundingRate` → `fundingRate`
- `fundingBias` → `fundingBias`
- `status` → `sourceCoinglassStatus`
- `timestamp` 可用于快照整合时的调试或日志，但最终以统一 `snapshotTime` 为主

---

## 十、Skill 使用规则
Skill 不应单独依赖 Funding 层做结论，而应把它当成增强证据。

### 正确使用方式
- Binance 主骨架先判断结构
- Funding 再补一层拥挤度判断

### 允许的用法
- “当前多头偏拥挤，继续追多风险上升”
- “当前空头偏拥挤，继续追空风险上升”

### 不允许的用法
- “Funding 偏高，所以现在一定该做空”
- “Funding 偏低，所以现在一定该做多”

---

## 十一、最小测试契约
为了确保 Funding Connector 真正可用，建议至少测试以下场景：

### 用例 1：标准交易对返回完整 Funding
输入：`LOBSTERUSDT`
预期：`status = ok`

### 用例 2：热门交易对返回完整 Funding
输入：`BTCUSDT`
预期：`status = ok`

### 用例 3：无效交易对
输入：`FAKEUSDT`
预期：`status = error`

### 用例 4：只拿到原始值，bias 缺失
预期：`status = partial`

### 用例 5：上游超时
预期：`status = error` 且带 `errorCode`

---

## 十二、当前阶段的结论
Coinglass Funding Connector 的最小接口契约应保持简单、清晰、可降级：

- 输入只收 `pair`
- 输出只返回 `fundingRate`、`fundingBias`、时间、状态
- 错误状态统一
- 空值规则统一
- 最终由后端映射进 `MarketSnapshot`

这样 Funding 层才能真正作为 Binance 主骨架之后的第一层增强，而不是一层口径混乱的附加信息。
