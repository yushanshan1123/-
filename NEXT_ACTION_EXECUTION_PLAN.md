# NEXT_ACTION_EXECUTION_PLAN.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档只回答一个问题：

> **接下来第一步到底干什么。**

不是继续扩文档，不是继续补概念，而是把下一步执行动作收束到最关键的一条主线上。

---

## 一、当前判断
当前项目最不缺的是：
- Skill 逻辑
- MVP 文档包
- 数据结构设计
- Connector 契约
- live 模式判定标准
- 实施路线图

当前项目最缺的是：
- **真实数据接入**
- **真实调用链路**
- **真实运行验证**

所以现在最合理的策略不是继续横向扩写，而是：

# 进入真实接入执行阶段

---

## 二、下一步唯一最高优先级

# P0：真实接通 Binance 主骨架

这是当前唯一最高优先级。

### 原因
因为只有这一步完成，项目才会第一次真正从：

- `logic_only`

进入：

- `live_ready` 的最低门槛准备阶段

如果 Binance 主骨架不接通，后面这些都无法真正成立：
- live 风控
- live 提醒增强
- 交易计划快照记录
- 后续 Funding / Heatmap 增强

---

## 三、这一步的明确目标
接下来这一轮执行，不追求所有增强层，
只追求一件事：

> **给一个 pair，系统能真实返回 Binance 主骨架数据，并映射成 `MarketSnapshot`。**

### 最小目标对象
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

---

## 四、这一步只做什么
本轮执行只做以下 4 件事：

### 1. 真正拉到 Binance 主骨架字段
必须包括：
- `price`
- `change24h`
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`

### 2. 映射成统一 `MarketSnapshot`
不能让 Skill 直接吃原始字段。

### 3. 让 Skill 能真实调用快照
至少先接到：
- 开仓前风控

### 4. 跑最小验收测试
至少验证：
- 标准交易对
- 热门交易对
- 无效交易对
- partial 降级
- error 降级

---

## 五、这一步明确不做什么
为了防止继续发散，这一轮先明确不做：

- 不接 Funding
- 不接 Heatmap
- 不碰 GMGN
- 不做复杂提醒调度
- 不做复杂记录与复盘查询
- 不做高级面板

### 原因
这些都应该建立在 Binance 主骨架已经真实可用的前提下。

---

## 六、执行顺序
建议下一步严格按以下顺序推进：

### Step 1
确认 Binance 主骨架字段入口

### Step 2
按 `BINANCE_CONNECTOR_API_CONTRACT.md` 固定最小输入输出

### Step 3
真实拉取 5 个核心字段

### Step 4
生成最小 `MarketSnapshot`

### Step 5
接入风控调用链

### Step 6
跑最小测试用例

### Step 7
根据测试结果更新状态板

---

## 七、完成标准
这一轮什么时候算完成，不靠感觉，靠下面 5 条：

### 完成标准
- [ ] 输入一个有效 `pair`，能真实返回 Binance 主骨架字段
- [ ] 能生成最小 `MarketSnapshot`
- [ ] 风控模块能真实读取该快照
- [ ] `partial` / `error` 能正确降级
- [ ] `IMPLEMENTATION_STATUS_BOARD.md` 可从 `not_started` 更新为更高状态

只要这 5 条成立，这一轮就算真正推进了。

---

## 八、当前阶段的执行纪律
为了避免项目继续散掉，建议接下来遵守三条纪律：

### 纪律 1
没有完成 Binance 主骨架前，不再继续扩增强层需求。

### 纪律 2
没有真实跑通调用链前，不把系统对外说成 live。

### 纪律 3
每完成一个阶段，优先更新状态板，而不是继续空扩文档。

---

## 九、这份文档的一句话结论
如果接下来只能做一件事，那就做：

# 先把 Binance 主骨架真实接通，并让风控模块真正吃到 `MarketSnapshot`

这一步一旦完成，
新币合约交易冷静器 2.1 才会第一次从“设计完整”进入“运行起点成立”。
