# COINGLASS_HEATMAP_API_CONTRACT.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于固定 **Coinglass Heatmap Connector** 的最小接口契约，避免后续开发时出现：

- 清算热力字段口径不一致
- “风险区在哪边”与“距离近不近”解释混乱
- 错误状态与 Binance / Funding 层不统一
- Skill 层不知道什么时候可以使用位置风险判断

核心目标是：

> **让清算热力这一层，成为一个可预测、可映射、可降级的位置风险增强接口。**

---

## 一、Connector 定位
Coinglass Heatmap Connector 的职责只有一个：

> **给一个交易对，返回当前位置最小可用的清算风险区判断。**

它负责：
- 读取清算热力原始信息
- 标准化成位置风险字段
- 返回状态

它不负责：
- 风控结论
- 提醒文案
- 用户交互
- 复盘分析

这些由后续业务层和 Skill 层完成。

---

## 二、最小接口名称建议
建议统一使用：

## `getCoinglassHeatmapRisk(pair)`

如果系统侧已抽象成统一市场快照增强层，也可以由上层包装成：

## `getMarketSnapshot(pair)` 的 Heatmap 子层

但在 Connector 这一层，建议保留明确语义：

> **这是 Heatmap Connector，不是通用市场接口。**

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
- 与 Binance / Funding 层保持同一套交易对口径

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
  "liquidationRiskZone": "above_price_high_density",
  "liquidationRiskDistance": "near",
  "timestamp": "2026-03-11T17:30:00Z",
  "status": "ok"
}
```

### 字段定义
#### `pair`
- 类型：string
- 含义：返回结果对应的交易对

#### `liquidationRiskZone`
- 类型：string | null
- 含义：当前价格附近，主要危险清算区位于哪一侧
- 建议值：
  - `above_price_high_density`
  - `below_price_high_density`
  - `two_sided_high_density`
  - `neutral`
  - `unknown`

#### `liquidationRiskDistance`
- 类型：string | null
- 含义：当前价格距离危险区的接近程度
- 建议值：
  - `near`
  - `medium`
  - `far`
  - `unknown`

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

## 五、风险字段定义规则

## 1. `liquidationRiskZone`
建议固定如下：

### `above_price_high_density`
表示：
- 当前价格上方存在明显清算密集区
- 做空时更容易先被向上扫掉

### `below_price_high_density`
表示：
- 当前价格下方存在明显清算密集区
- 做多时更容易先被向下探掉

### `two_sided_high_density`
表示：
- 当前上下两侧都不干净
- 市场更容易来回扫

### `neutral`
表示：
- 当前没有明显的高密度危险区
- 不能从热力层得出明显位置风险提示

### `unknown`
表示：
- 当前热力层不可用
- 或无法可靠判断风险区方向

---

## 2. `liquidationRiskDistance`
建议固定如下：

### `near`
表示：
- 当前位置离危险区较近
- 开仓更容易先被扫

### `medium`
表示：
- 有位置风险，但不是贴脸风险

### `far`
表示：
- 当前离危险区相对较远
- 短时间内不是最直接的压力

### `unknown`
表示：
- 当前无法可靠判断距离

---

## 六、状态定义

## 1. `ok`
表示：
- Connector 已成功返回风险区判断
- 且已成功返回距离判断

### 判定条件
以下字段应存在且可用：
- `liquidationRiskZone`
- `liquidationRiskDistance`
- `timestamp`

---

## 2. `partial`
表示：
- Connector 只获取到了部分热力层信息
- 可作为有限位置提示，但不足以支持完整位置判断

### 典型情况
- 已能判断 `liquidationRiskZone`
- 但 `liquidationRiskDistance` 无法可靠给出

### 原则
- 已拿到的字段可以返回
- 未拿到的字段必须为 `null` 或 `unknown`
- 不能伪装成 `ok`

---

## 3. `error`
表示：
- Connector 无法提供可用热力层结果
- 不应作为当前位置风险依据

### 典型情况
- 输入非法
- Coinglass 请求失败
- 上游超时
- 原始热力层解析失败

### 原则
- 不返回伪造值
- 允许附带错误说明字段

---

## 七、错误输出契约

### 建议错误输出
```json
{
  "pair": "LOBSTERUSDT",
  "liquidationRiskZone": null,
  "liquidationRiskDistance": null,
  "timestamp": "2026-03-11T17:31:00Z",
  "status": "error",
  "errorCode": "UPSTREAM_ERROR",
  "errorMessage": "Heatmap data unavailable from Coinglass"
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

## 1. 枚举字段统一规则
#### `liquidationRiskZone`
必须使用固定枚举，不允许自由文本。

#### `liquidationRiskDistance`
必须使用固定枚举，不允许自由文本。

### 原因
- 避免后续 Skill 文案分支混乱
- 避免一个开发写 `high_above`，另一个写 `above_dense_zone`

---

## 2. 时间字段规则
#### `timestamp`
必须：
- 使用 UTC
- 使用 ISO 8601 格式

例如：
- `2026-03-11T17:30:00Z`

---

## 3. 空值规则
如果字段拿不到：
- 必须明确返回 `null` 或 `unknown`
- 不允许省略关键字段

特别是：
- `liquidationRiskZone`
- `liquidationRiskDistance`

---

## 九、与 `MarketSnapshot` 的映射契约
Heatmap Connector 输出不是最终给 Skill 的对象。
后端应将其映射进统一 `MarketSnapshot`。

### 映射示例
```json
{
  "liquidationRiskZone": "above_price_high_density",
  "liquidationRiskDistance": "near",
  "sourceCoinglassStatus": "ok"
}
```

### 映射规则
- `liquidationRiskZone` → `liquidationRiskZone`
- `liquidationRiskDistance` → `liquidationRiskDistance`
- `status` → `sourceCoinglassStatus`
- `timestamp` 可用于日志、调试或快照整合，但最终统一快照时间仍以 `snapshotTime` 为主

---

## 十、Skill 使用规则
Skill 不应把热力层当成方向预测工具，而应把它当成位置风险增强层。

### 正确使用方式
- Binance 主骨架先看结构
- Funding 再看拥挤
- Heatmap 再看位置是否舒服

### 允许的用法
- “当前上方有高密度清算区，做空容易先被扫”
- “当前下方风险区较近，做多不算舒服”
- “上下两侧都不干净，更像来回扫的区域”

### 不允许的用法
- “上方有清算区，所以一定会先涨”
- “下方有清算区，所以现在一定该做多”

---

## 十一、最小测试契约
为了确保 Heatmap Connector 真正可用，建议至少测试以下场景：

### 用例 1：标准交易对返回完整风险层
输入：`LOBSTERUSDT`
预期：`status = ok`

### 用例 2：热门交易对返回完整风险层
输入：`BTCUSDT`
预期：`status = ok`

### 用例 3：无效交易对
输入：`FAKEUSDT`
预期：`status = error`

### 用例 4：只判断出风险区，距离缺失
预期：`status = partial`

### 用例 5：上游超时
预期：`status = error` 且带 `errorCode`

---

## 十二、当前阶段的结论
Coinglass Heatmap Connector 的最小接口契约应保持简单、固定、可降级：

- 输入只收 `pair`
- 输出只返回风险区、风险距离、时间、状态
- 错误状态统一
- 枚举口径统一
- 最终由后端映射进 `MarketSnapshot`

这样清算热力层才能真正作为 Funding 之后的位置风险增强层，而不是一层难以稳定使用的模糊信息。
