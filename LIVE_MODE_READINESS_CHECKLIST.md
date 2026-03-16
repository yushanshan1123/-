# LIVE_MODE_READINESS_CHECKLIST.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **什么时候，系统才算真正进入 live-data 模式。**

这很重要，因为“写了 live 逻辑”不等于“真的 live 了”。

---

## 一、三种运行状态
建议系统统一只认三种状态：

### 1. `logic_only`
没有实时数据能力，或当前请求无法可靠读取核心实时数据。

### 2. `partial_live`
已有真实核心 live 数据，但增强层不完整、不可用或不稳定。

### 3. `live_ready`
核心主骨架稳定接通，Skill 真正使用，且降级规则跑通。

---

## 二、当前阶段最新判断
按照目前仓库真实状态，这个项目当前最准确的运行判断应为：

# `live_ready`（核心主骨架）

同时必须带一句增强层说明：

> **当前 Binance 主骨架已真实接通；Funding 与 Heatmap 仅处于可降级增强层骨架状态；GMGN 未接入。**

也就是说，现在不是：
- `logic_only`

也不是：
- full enhanced live

而是：
- **Core live-ready**
- **Enhancement layers partial / unavailable**

---

## 三、进入 `live_ready` 的最低条件
只有当以下所有条件都成立时，才允许进入核心 `live_ready`。

### A. Binance 主骨架条件
必须全部满足：
- `price` 可用
- `change24h` 可用
- `longShortRatio` 可用
- `openInterest` 可用
- `topTraderLongShortRatio` 可用
- `snapshotTime` 可用
- `sourceBinanceStatus` 可用

### B. 统一对象条件
必须全部满足：
- 后端可生成统一 `MarketSnapshot`
- `symbol` / `pair` / `snapshotTime` 映射正确
- `sourceBinanceStatus` 映射正确
- 空值规则一致

### C. Skill 使用条件
必须全部满足：
- CLI / 统一入口 / runtime / 本地样板已实际读取 `MarketSnapshot`
- live 风控已实际使用快照
- 缺失增强层时不会伪造值

### D. 降级条件
必须全部满足：
- Funding / Heatmap 不可用时能返回 `null` + `error` 状态
- 不会把增强层 error 伪装成可用
- 对外表述不会夸大能力

---

## 四、增强层状态定义
### Level 1：Core live-ready
表示：
- Binance 主骨架 ready

### Level 2：Core live + Funding
表示：
- Binance 主骨架 ready
- Funding 真实可用

### Level 3：Core live + Funding + Heatmap
表示：
- Binance 主骨架 ready
- Funding 真实可用
- Heatmap 真实可用

### Level 4：Full enhanced live
表示：
- Binance 主骨架 ready
- Funding 真实可用
- Heatmap 真实可用
- GMGN 或其他增强层也真实可用

---

## 五、当前项目的真实口径
当前建议对外统一使用以下口径：

### 正确说法
- 当前已进入 **Binance core live-ready**
- Funding 与 Heatmap 当前为**可降级增强层骨架**
- GMGN 当前未接入 / blocked

### 不正确说法
- 当前四层都已真实接通
- 当前已具备完整增强版 live
- 当前已包含 GMGN 聪明钱层

---

## 六、当前结论
一句话结论：

> **当前系统已经进入核心 `live_ready`（基于 Binance 主骨架），但 Funding / Heatmap 仍是增强层骨架且当前不可用，GMGN 仍 blocked，因此还不能宣称完整增强版 live。**
