# BINANCE_CONNECTOR_IMPLEMENTATION_STEPS.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于把当前已经完成的：

- Binance 可行性验证
- 字段映射验证
- Connector 契约定义
- Phase 1 任务拆解

继续往前推进一步，回答一个更实际的问题：

> **现在怎么从“已验证接口”走到“可运行的 Binance Connector 原型”。**

这份文档不再讲方向，而是讲实施路径。

---

## 一、当前起点
目前已经具备的基础包括：

### 已有
- Binance 主骨架字段已确定
- Binance 公共接口已验证可用
- 字段与接口映射已验证
- Connector 输入输出契约已定义
- `MarketSnapshot` 最小结构已定义
- Phase 1 的优先级与任务表已完成

### 还缺
- 把多个接口真实拼起来
- 统一清洗字段
- 生成最小 Connector 输出
- 生成最小 `MarketSnapshot`
- 接到 Skill 调用链

也就是说，当前真正缺的是：

> **把已知正确的零件拼成一个能跑的最小原型。**

---

## 二、这一轮实施的最小目标
这一轮不追求完整后端，只追求最小可运行原型。

### 最小成功标准
给一个交易对，例如 `BTCUSDT`，系统能返回：

```json
{
  "pair": "BTCUSDT",
  "price": 70544.80,
  "change24h": -0.283,
  "longShortRatio": 1.1349,
  "openInterest": 82994.727,
  "topTraderLongShortRatio": 1.0074,
  "timestamp": "2026-03-11T17:39:00Z",
  "status": "ok"
}
```

然后再映射为：

```json
{
  "symbol": "BTC",
  "pair": "BTCUSDT",
  "snapshotTime": "2026-03-11T17:39:00Z",
  "price": 70544.80,
  "change24h": -0.283,
  "longShortRatio": 1.1349,
  "openInterest": 82994.727,
  "topTraderLongShortRatio": 1.0074,
  "sourceBinanceStatus": "ok"
}
```

---

## 三、建议实施顺序
建议按下面 6 步推进。

---

## Step 1：先做最小抓取脚本
### 目标
不要一上来就做复杂后端，先做一个最小脚本，把 4 个已验证接口打通。

### 这一步要完成什么
输入：
- `pair`

输出：
- 原始接口返回结果合集

### 脚本至少要请求这几个接口
1. `/fapi/v1/ticker/24hr`
2. `/futures/data/globalLongShortAccountRatio`
3. `/fapi/v1/openInterest`
4. `/futures/data/topLongShortPositionRatio`

### 完成标志
能够用一个脚本拿回这四份原始数据。

---

## Step 2：做字段清洗与类型转换
### 目标
把上游原始字符串字段，清洗成内部标准类型。

### 这一步要完成什么
- `lastPrice` → `price:number`
- `priceChangePercent` → `change24h:number`
- `longShortRatio` → `longShortRatio:number`
- `openInterest` → `openInterest:number`
- `longShortRatio(top trader)` → `topTraderLongShortRatio:number`

### 重点注意
- 所有数字必须转成 `number`
- 不能把字符串数字直接透传
- 数组接口先取最新一条

### 完成标志
得到一份清洗后的内部对象。

---

## Step 3：补统一时间与状态字段
### 目标
让 Connector 输出真正符合契约，而不是只有几项数字。

### 这一步要完成什么
- 生成统一 `timestamp`
- 根据字段完整度判断：
  - `ok`
  - `partial`
  - `error`

### 判定原则
#### `ok`
5 个核心字段都有

#### `partial`
有价格层，但结构层缺部分字段

#### `error`
价格层都失败，或输入非法

### 完成标志
Connector 输出第一次具备“可被业务层消费”的形态。

---

## Step 4：映射成最小 `MarketSnapshot`
### 目标
不要让 Skill 直接读 Connector 输出，而是继续映射到统一市场对象。

### 这一步要完成什么
- `pair` 保留
- 从 `pair` 推导 `symbol`
- `timestamp` → `snapshotTime`
- `status` → `sourceBinanceStatus`

### 完成标志
得到最小 `MarketSnapshot`。

---

## Step 5：先接一条最小业务链
### 目标
不要一口气接全系统，先只接一条最重要的链路：

# 开仓前风控

### 原因
风控是当前 MVP 的核心价值点，且最适合验证 live 快照有没有真正被用起来。

### 这一步要完成什么
- 用户输入 `pair`
- 系统读取 `getMarketSnapshot(pair)`
- Skill 根据 `ok / partial / error` 输出不同风控口径

### 完成标志
至少有一条 live 风控链能跑通。

---

## Step 6：跑最小测试集
### 目标
确保不是“脚本跑过一次”，而是真的具备最小可用性。

### 必测场景
#### 场景 1
`BTCUSDT` 返回完整字段

#### 场景 2
一个有效新币 / 目标币对返回完整字段

#### 场景 3
`FAKEUSDT` 返回 `error`

#### 场景 4
人为模拟部分字段缺失，触发 `partial`

#### 场景 5
Skill 在 `ok / partial / error` 下输出正确

### 完成标志
项目第一次具备“可验证的 live 基础能力”。

---

## 四、这一轮最适合的实施形式
当前最适合的不是直接做完整服务，而是：

## 推荐形式
先做：
- 一个最小 Python 原型脚本
- 或一个最小 Node 原型脚本

先证明：
- 可以稳定抓数据
- 可以稳定清洗
- 可以稳定映射

然后再决定是否封装成更正式的后端函数。

### 为什么这样更好
因为你现在最需要的是：
- 快速验证链路
- 尽快拿到第一版 live 原型
- 避免先陷入工程化细节

---

## 五、这一轮明确不做什么
为了不继续发散，这一轮明确不做：

- 不接 Funding
- 不接 Heatmap
- 不碰 GMGN
- 不做提醒调度
- 不做完整数据库存储
- 不做完整后台服务框架

### 原因
当前目标只有一个：

> **先跑通 Binance 主骨架 → Connector → MarketSnapshot → 风控 这条最小 live 链路。**

---

## 六、当前阶段一句话结论
从实施角度看，下一步最合理的动作不是再补解释，而是：

# 先写一个最小 Binance Connector 原型脚本，把 4 个已验证接口拼成一个可返回最小 `MarketSnapshot` 的原型

这一步一旦跑通，项目就会第一次真正从“文档齐全”进入“live 原型成立”。
