# BINANCE_CONNECTOR_API_CONTRACT.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于固定 **Binance Connector** 的最小接口契约，避免后续开发时出现：

- 输入结构反复变化
- 字段名来回修改
- 错误状态不统一
- Skill 层不知道该如何读取

核心目标是：

> **让 Binance 主骨架的数据获取层，有一个可预测、可对接、可测试的标准输入输出。**

---

## 一、Connector 定位
Binance Connector 的职责只有一个：

> **给一个交易对，返回当前这一刻的 Binance 主骨架市场数据。**

它负责：
- 拉取原始数据
- 标准化字段
- 返回状态

它不负责：
- 风控判断
- 提醒文案
- 交易复盘
- 用户交互

这些由后续业务层和 Skill 层完成。

---

## 二、最小接口名称建议
建议统一使用：

## `getBinanceMarketCore(pair)`

如果系统侧已经统一抽象成市场快照读取层，也可以由上层包装成：

## `getMarketSnapshot(pair)`

但在 Connector 这一层，建议先保留明确语义：

> **这是 Binance 主骨架 Connector，不是通用业务接口。**

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
- 不接受模糊 symbol（例如仅 `LOBSTER`）作为 Connector 最小输入

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
  "price": 0.1234,
  "change24h": 18.2,
  "longShortRatio": 1.34,
  "openInterest": 245000000,
  "topTraderLongShortRatio": 0.91,
  "timestamp": "2026-03-11T17:00:00Z",
  "status": "ok"
}
```

### 字段定义
#### `pair`
- 类型：string
- 含义：返回结果对应的交易对

#### `price`
- 类型：number | null
- 含义：当前价格

#### `change24h`
- 类型：number | null
- 含义：24 小时涨跌幅

#### `longShortRatio`
- 类型：number | null
- 含义：多空持仓人数比

#### `openInterest`
- 类型：number | null
- 含义：合约持仓量（OI）

#### `topTraderLongShortRatio`
- 类型：number | null
- 含义：大户持仓多空比

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

## 五、状态定义

## 1. `ok`
表示：
- Connector 已成功获取并标准化所有 P0 核心字段

### 判定条件
以下字段都应存在且非空：
- `price`
- `change24h`
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`

---

## 2. `partial`
表示：
- Connector 获取到了部分数据
- 但结构层不完整，不能被当成完整 live 结构使用

### 典型情况
- 有 `price`
- 有 `change24h`
- 但缺 `openInterest` 或 `topTraderLongShortRatio`

### 原则
- 已拿到的字段可以返回
- 未拿到的字段必须为 `null`
- 不能伪装成 `ok`

---

## 3. `error`
表示：
- Connector 无法为当前请求提供有效结果
- 不能作为 live 判断依据

### 典型情况
- `pair` 非法
- Binance 数据源请求失败
- 核心价格层失败
- 无法生成有效时间戳

### 原则
- 不返回伪造值
- 允许返回错误说明字段（见下文扩展）

---

## 六、错误输出契约

### 建议错误输出
```json
{
  "pair": "FAKEUSDT",
  "price": null,
  "change24h": null,
  "longShortRatio": null,
  "openInterest": null,
  "topTraderLongShortRatio": null,
  "timestamp": "2026-03-11T17:05:00Z",
  "status": "error",
  "errorCode": "PAIR_NOT_FOUND",
  "errorMessage": "Binance market core data unavailable for pair"
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

## 七、字段级规则

## 1. 数值字段统一规则
以下字段必须统一为 number 或 null：
- `price`
- `change24h`
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`

### 不允许
- 字符串数字直接原样透传
- 带单位文本
- 百分号字符串

### 例如
允许：
- `18.2`

不允许：
- `"18.2%"`
- `"18.2"`

---

## 2. 时间字段规则
#### `timestamp`
必须：
- 使用 UTC
- 使用 ISO 8601 格式

例如：
- `2026-03-11T17:00:00Z`

---

## 3. 空值规则
如果字段拿不到：
- 必须明确返回 `null`
- 不允许省略关键字段

原因：
- 省略字段会让 Skill 层和映射层更难判断状态

---

## 八、与 `MarketSnapshot` 的映射契约
Connector 输出不是最终给 Skill 的对象。
后端应将其映射为统一 `MarketSnapshot`。

### 映射示例
```json
{
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "snapshotTime": "2026-03-11T17:00:00Z",
  "price": 0.1234,
  "change24h": 18.2,
  "longShortRatio": 1.34,
  "openInterest": 245000000,
  "topTraderLongShortRatio": 0.91,
  "sourceBinanceStatus": "ok"
}
```

### 映射规则
- `pair` → `pair`
- 从 `pair` 推导 `symbol`
- `timestamp` → `snapshotTime`
- `status` → `sourceBinanceStatus`
- 数值字段直接透传

---

## 九、Skill 使用规则
Skill 不应该直接理解 Binance 原始字段来源，只应该读取统一对象。

### 正确链路
1. 用户提供 `pair`
2. 系统调用 `getBinanceMarketCore(pair)`
3. 后端映射为 `MarketSnapshot`
4. Skill 读取 `MarketSnapshot`
5. 根据 `sourceBinanceStatus` 决定：
   - live 判断
   - partial 判断
   - logic-only 降级

---

## 十、最小测试契约
为了确保这个 Connector 真正可用，建议至少测试以下场景：

### 用例 1：标准交易对
输入：`LOBSTERUSDT`
预期：`status = ok`

### 用例 2：热门交易对
输入：`BTCUSDT`
预期：`status = ok`

### 用例 3：无效交易对
输入：`FAKEUSDT`
预期：`status = error`

### 用例 4：部分字段缺失
预期：`status = partial`

### 用例 5：上游超时
预期：`status = error` 且带 `errorCode`

---

## 十一、当前阶段的结论
Binance Connector 的最小接口契约应保持简单、稳定、可验证：

- 输入只收 `pair`
- 输出只返回主骨架字段 + 时间 + 状态
- 错误状态统一
- 空值规则统一
- 最终由后端映射成 `MarketSnapshot`

这份契约一旦固定，后续 Skill、测试、数据层、日志层就都可以围绕同一套口径推进。
