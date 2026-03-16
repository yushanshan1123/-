# SERVICE_MIGRATION_PHASE1_PLAN.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档只聚焦第一批正式化迁移，回答一个问题：

> **现在应该怎么把原型里的 Binance + live 风控，迁成第一批正式 service。**

这份文档不追求覆盖全系统，
只盯最关键的两层：

- `market_data_service`
- `risk_check_service`

原因很简单：

> 这两层是当前整条 MVP 原型闭环的底座。  
> 不先把底座正式化，后面提醒、记录、复盘都只能继续停在原型脚本层。

---

## 一、Phase 1 范围
Phase 1 只做两件事：

### 1. 正式化市场数据层
把当前原型里的 Binance 主骨架读取，收敛成正式 `market_data_service`。

### 2. 正式化风控层
把当前原型里的 live 风控逻辑，收敛成正式 `risk_check_service`。

---

## 二、Phase 1 明确不做什么
为了不继续发散，这一阶段先明确不做：

- 不正式化提醒调度
- 不正式化记录存储
- 不正式化复盘查询
- 不接 Funding
- 不接 Heatmap
- 不碰 GMGN
- 不引入复杂数据库设计

### 原因
当前最需要的不是把所有模块都拉进正式化，
而是：

> **先把“数据 → 风控”这条底座链正式化。**

---

## 三、Phase 1 的目标结果
完成后，系统应至少具备：

### 目标 1
存在一个正式的：
- `market_data_service`

能够稳定提供：
- `getMarketSnapshot(pair)`

### 目标 2
存在一个正式的：
- `risk_check_service`

能够稳定提供：
- `runRiskCheck(plan)`

### 目标 3
这两个 service 不再依赖“演示脚本入口”才能工作。

---

## 四、当前原型到 Phase 1 服务的迁移关系

### 当前原型来源
- `binance_connector_prototype.py`
- `xinbi_live.py`
- `live_risk_check_prototype.py`
- `xinbi_cli.py`

### 迁移目标
#### 迁入 `market_data_service`
- Binance 主骨架读取
- `MarketSnapshot` 组装
- 快照状态判断

#### 迁入 `risk_check_service`
- 输入标准化
- 风险评分逻辑
- 风控报告生成
- 风控结构化输出

#### 暂时保留在原型层
- CLI 演示入口
- 单独原型脚本

---

## 五、`market_data_service` 的 Phase 1 目标

## 1. 目标职责
在 Phase 1，`market_data_service` 只负责：
- 调用 Binance 主骨架数据
- 清洗字段
- 生成统一 `MarketSnapshot`
- 返回状态

## 2. 最小函数目标
建议至少有：

### `get_market_snapshot(pair)`
输入：
- `pair`

输出：
- 标准 `MarketSnapshot`

### `get_binance_market_core(pair)`
输入：
- `pair`

输出：
- Binance 主骨架原始标准化结果

## 3. Phase 1 完成标志
- 市场快照逻辑已从 CLI / 演示脚本中抽离
- 可被别的 service 直接调用
- 状态值与字段规则继续保持一致

---

## 六、`risk_check_service` 的 Phase 1 目标

## 1. 目标职责
在 Phase 1，`risk_check_service` 只负责：
- 标准化交易计划输入
- 基于 `MarketSnapshot` 做风险判断
- 返回结构化风控结果
- 生成用户可读文本

## 2. 最小函数目标
建议至少有：

### `normalize_plan_input(plan)`
把自然输入统一成内部标准计划对象。

### `assess_risk(plan, snapshot)`
生成：
- 风险等级
- 冲突点
- 建议

### `build_risk_report(plan, snapshot)`
生成：
- 用户可读风控文本

### `run_risk_check(plan)`
整体执行：
- 标准化输入
- 读取快照
- 输出完整结果

## 3. Phase 1 完成标志
- 风控逻辑已从演示脚本中抽离
- 风控结果可独立被 Skill / API / CLI 调用
- `mode` / `riskResult` / `report` 输出结构固定

---

## 七、建议目录思路（逻辑层面）
现在不一定马上改目录，但建议心里先按这个结构迁：

```text
services/
  market_data_service/
    __init__.py
    binance_connector.py
    market_snapshot.py

  risk_check_service/
    __init__.py
    normalize.py
    assess.py
    report.py
```

### 说明
这里不是要求现在立刻重构成复杂工程，
而是为了在迁移时始终有目标骨架。

---

## 八、Phase 1 具体迁移步骤
建议按这个顺序迁。

### Step 1：抽离 `market_data_service`
从：
- `binance_connector_prototype.py`
- `xinbi_live.py`

抽出：
- 快照读取相关逻辑
- Binance 主骨架相关逻辑

### Step 2：固定 `MarketSnapshot` 出口
确保所有调用统一只认：
- `get_market_snapshot(pair)`

### Step 3：抽离 `risk_check_service`
从：
- `xinbi_live.py`
- `live_risk_check_prototype.py`

抽出：
- 输入标准化
- 风险评估
- 风控报告生成

### Step 4：保留原 CLI，但改为只调用 service
让：
- `xinbi_cli.py`

不再自己承载逻辑，
而只是调用正式 service。

### Step 5：回归验证
至少验证：
- `snapshot`
- `risk-check`
- `skill-risk-check`

在迁移后仍能正常输出。

---

## 九、Phase 1 的验收标准
只看这 5 条：

- [ ] 已存在清晰的 `market_data_service` 边界
- [ ] 已存在清晰的 `risk_check_service` 边界
- [ ] CLI 入口不再承载核心逻辑
- [ ] 快照输出格式未被破坏
- [ ] 风控输出格式未被破坏

满足这 5 条，就说明第一批正式化迁移成立。

---

## 十、Phase 1 完成后的意义
如果这一阶段完成，你会获得三件事：

### 1. 原型底座稳定下来
以后不再每补一个功能，就继续把逻辑塞回脚本里。

### 2. 后续正式接 Skill 会更顺
因为 Skill 只需要调用：
- 市场快照服务
- 风控服务

### 3. 后续提醒 / 记录 / 复盘迁移会更简单
因为它们终于有稳定底层可以依赖了。

---

## 十一、当前阶段一句话结论
Phase 1 最正确的推进方式不是继续加新原型，
而是：

> **先把 Binance 主骨架和 live 风控，从“可跑原型”迁成“可复用正式 service”，把底座稳住。**

这是新币合约交易冷静器 2.1 从原型闭环走向正式 MVP 的第一步正式迁移。
