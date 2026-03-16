# BINANCE_REAL_INTEGRATION_TASKLIST.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
把 **Binance 主骨架真实接入** 这件事，从“方向正确”继续拆成“可以逐项执行”的任务表。

这份文档只聚焦 Phase 1：

> **先把 Binance 的实时主骨架接通，让 Skill 真正拥有 live 基础能力。**

---

## 一、Phase 1 目标
Phase 1 完成后，后端对任意一个有效交易对，例如 `LOBSTERUSDT`，应能稳定生成最小 `MarketSnapshot`：

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

Skill 后续只读这个统一对象，不直接依赖原始 Binance 响应。

---

## 二、Phase 1 必做字段
### P0 核心字段
- `price`
- `change24h`
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`
- `snapshotTime`
- `sourceBinanceStatus`

### P0 关联字段
- `symbol`
- `pair`

---

## 三、任务拆解总览
Phase 1 建议拆成 8 个任务块：

1. 锁定字段与状态定义
2. 确认每个字段的数据入口
3. 设计 BinanceConnector 输入输出
4. 拉取并标准化原始字段
5. 映射生成 `MarketSnapshot`
6. 定义降级与错误处理
7. 接到 Skill 调用入口
8. 设计测试与验收清单

---

## 四、任务块 1：锁定字段与状态定义
### 任务目标
先把第一阶段所有字段名、状态名、缺失规则固定下来，不再边做边改。

### 具体任务
- 固定 `price` 字段名
- 固定 `change24h` 字段名
- 固定 `longShortRatio` 字段名
- 固定 `openInterest` 字段名
- 固定 `topTraderLongShortRatio` 字段名
- 固定 `snapshotTime` 字段名
- 固定 `sourceBinanceStatus` 枚举值

### 状态建议
- `ok`
- `partial`
- `error`

### 完成标志
字段和状态命名不再变化。

---

## 五、任务块 2：确认每个字段的数据入口
### 任务目标
让每个字段都明确“从哪里来”。

### 具体任务
- 确认 `price` 的数据入口
- 确认 `change24h` 的数据入口
- 确认 `longShortRatio` 的数据入口
- 确认 `openInterest` 的数据入口
- 确认 `topTraderLongShortRatio` 的数据入口

### 输出要求
形成一张最终对应表：

| 字段 | 数据入口 | 是否必需 | 备注 |
|---|---|---|---|
| price | Binance | 是 | P0 |
| change24h | Binance | 是 | P0 |
| longShortRatio | Binance | 是 | P0 |
| openInterest | Binance | 是 | P0 |
| topTraderLongShortRatio | Binance | 是 | P0 |

### 完成标志
不再存在“这个字段到时候再找”的状态。

---

## 六、任务块 3：设计 BinanceConnector 输入输出
### 任务目标
先把 Connector 设计成一个清晰、稳定、最小的层。

### 输入建议
```json
{
  "pair": "LOBSTERUSDT"
}
```

### 输出建议
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

### 具体任务
- 固定 Connector 输入结构
- 固定 Connector 输出结构
- 固定时间字段格式
- 固定错误返回格式

### 完成标志
给一个 `pair`，Connector 的返回格式可预测、可调试。

---

## 七、任务块 4：拉取并标准化原始字段
### 任务目标
把 Binance 原始数据真正拿下来，并规范成内部一致格式。

### 具体任务
#### 4.1 价格层
- 拉取实时价格
- 拉取 24h 涨跌
- 统一数值类型

#### 4.2 结构层
- 拉取多空持仓人数比
- 拉取 OI
- 拉取大户多空比
- 统一数值类型

#### 4.3 时间层
- 生成统一采集时间
- 统一成 ISO 时间字符串

### 完成标志
Connector 输出里 5 个核心字段都能正常落位。

---

## 八、任务块 5：映射生成 `MarketSnapshot`
### 任务目标
不要让 Skill 直接碰 Connector 原始结果，而是统一映射成 `MarketSnapshot`。

### 具体任务
- 从 `pair` 推导 `symbol`
- 将 `timestamp` 映射为 `snapshotTime`
- 将 `status` 映射为 `sourceBinanceStatus`
- 将所有字段放入统一快照对象

### 最小结果
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

### 完成标志
Skill 拿到的已经不是 Binance 碎片字段，而是统一对象。

---

## 九、任务块 6：定义降级与错误处理
### 任务目标
避免数据缺失时系统装懂。

### 具体任务
#### 情况 A：全部字段都有
- `sourceBinanceStatus = ok`

#### 情况 B：只有价格层，缺结构层部分字段
- `sourceBinanceStatus = partial`
- Skill 只能做基础行情判断

#### 情况 C：价格都拿不到
- `sourceBinanceStatus = error`
- Skill 退回 logic-only 模式

### 规则要求
- 不能伪造字段
- 不能拿旧值冒充新值
- 不能因为少一个字段就默认一切正常

### 完成标志
缺数据时，Skill 能清楚声明自己当前判断层级。

---

## 十、任务块 7：接到 Skill 调用入口
### 任务目标
让 Skill 真正用上 live 快照，而不是只停留在设计层。

### 建议入口
- `getMarketSnapshot(pair)`

### 具体任务
- Skill 做新币速评前先读快照
- Skill 做风控前先读快照
- Skill 记录交易计划时保存快照

### 使用顺序
1. 用户给出 `pair`
2. 系统调用 `getMarketSnapshot(pair)`
3. 若 `ok` 或 `partial`，进入 live 判断
4. 若 `error`，退回 logic-only 模式

### 完成标志
Skill 已真正有 live / logic 两套分支，而不是只写在文档里。

---

## 十一、任务块 8：测试与验收
### 任务目标
保证不是“理论接通”，而是“可验证接通”。

### 必测场景
#### 场景 1：标准交易对返回完整字段
输入：`LOBSTERUSDT`
输出：5 个核心字段完整

#### 场景 2：热门标准对返回完整字段
输入：`BTCUSDT`
输出：5 个核心字段完整

#### 场景 3：无效交易对
输入：`FAKEUSDT`
输出：错误状态，不伪造值

#### 场景 4：部分字段缺失
输出：`partial`，并触发 Skill 降级

### 验收标准
- Connector 稳定返回
- `MarketSnapshot` 映射正确
- Skill 能引用这些字段输出风控
- 缺字段时能正确降级

---

## 十二、建议执行顺序
如果要真正推进，我建议按下面的顺序做：

### Step 1
先完成：字段命名、状态命名、输入输出结构固定

### Step 2
确认每个字段的数据入口

### Step 3
先打通价格层：
- `price`
- `change24h`

### Step 4
再打通结构层：
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`

### Step 5
生成统一 `MarketSnapshot`

### Step 6
接到 Skill 调用入口

### Step 7
跑测试用例和验收

---

## 十三、当前阶段一句话结论
Phase 1 的任务不是“把所有增强数据都接完”，而是：

> **先让新币合约交易冷静器 2.1 真实拥有 Binance 主骨架数据。**

只要这一步完成，Skill 就会从“逻辑版”真正进入“live 基础版”。
