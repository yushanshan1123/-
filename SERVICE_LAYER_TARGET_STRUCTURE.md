# SERVICE_LAYER_TARGET_STRUCTURE.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **当当前原型链逐步正式化时，目标服务层结构应该长什么样。**

它解决的问题不是“要不要做”，而是：
- 正式模块应该怎么分层
- 哪些逻辑应该归到哪个 service
- 哪些东西不该继续混在一个脚本里
- 原型迁移时应该往哪里放

---

## 一、为什么现在需要服务层结构
当前项目已经有：
- Binance Connector 原型
- live 风控原型
- 提醒分流原型
- 记录原型
- 复盘原型

这些原型已经证明了方向可行。  
但如果继续只靠脚本叠加，会出现这些问题：

- 逻辑越来越散
- 调用边界不清楚
- 一个脚本做太多事
- 后续接 Skill / 后端时会越来越难维护

所以现在需要提前把目标服务层结构定出来。

---

## 二、目标服务层总览
建议正式化后，核心服务层拆成 5 个主服务：

1. `market_data_service`
2. `risk_check_service`
3. `alert_service`
4. `record_service`
5. `review_service`

如果后续继续扩展，还可补：

6. `integration_service`
7. `skill_entry_service`

---

## 三、推荐分层图
可以把目标结构理解成：

### 数据源层
- Binance
- Coinglass
- GMGN（若可行）

↓

### 集成层
- `integration_service`

↓

### 统一数据层
- `market_data_service`

↓

### 业务服务层
- `alert_service`
- `risk_check_service`
- `record_service`
- `review_service`

↓

### 技能 / 调用入口层
- `skill_entry_service`
- CLI / API / 调度入口

---

## 四、各服务的职责边界

## 1. `market_data_service`
### 作用
负责：
- 获取市场主骨架数据
- 统一生成 `MarketSnapshot`
- 对外提供市场快照读取能力

### 它应该包含
- Binance 主骨架读取
- Funding / Heatmap 后续映射入口
- `getMarketSnapshot(pair)`

### 它不应该负责
- 风控逻辑
- 提醒文案
- 记录写入
- 复盘判断

### 当前原型迁移来源
- `binance_connector_prototype.py`
- `xinbi_live.py` 中的快照读取部分

---

## 2. `risk_check_service`
### 作用
负责：
- 接收标准化交易计划
- 读取 `MarketSnapshot`
- 生成结构化风控结果
- 输出用户可读报告

### 它应该包含
- 计划标准化
- 风险等级判断
- 冲突点整理
- 冷静建议生成

### 它不应该负责
- 直接拉原始 Binance 接口
- 直接写记录文件
- 直接发送消息

### 当前原型迁移来源
- `xinbi_live.py` 中的风险判断逻辑
- `live_risk_check_prototype.py`

---

## 3. `alert_service`
### 作用
负责：
- 生成提醒消息
- 管理提醒后的分流入口
- 连接“提醒 → 速评 / 风控”两条支线

### 它应该包含
- 公告提醒文案生成
- 提醒分流逻辑
- 后续提醒状态回写入口

### 它不应该负责
- 市场数据抓取
- 风控判断细节
- 复盘逻辑

### 当前原型迁移来源
- `alert_to_risk_prototype.py`
- `alert_to_review_prototype.py`
- `ALERT_MESSAGE_TEMPLATE.md`

---

## 4. `record_service`
### 作用
负责：
- 创建 `TradeReviewRecord`
- 保存交易计划
- 保存风控时刻快照
- 读取交易记录

### 它应该包含
- `createTradeReviewRecord(record)`
- `getTradeReviewRecord(tradeId)`
- `listTradeReviewRecords(userId, filters)`

### 它不应该负责
- 风控判断
- 复盘结论生成
- 提醒发送

### 当前原型迁移来源
- `risk_to_record_prototype.py`
- `trade_review_records.json`

---

## 5. `review_service`
### 作用
负责：
- 读取交易记录
- 更新交易结果
- 生成复盘结论

### 它应该包含
- `updateTradeResult(tradeId, result)`
- `buildTradeReview(record)`
- `reviewLatestTrade(userId)`

### 它不应该负责
- 原始快照抓取
- 提醒发送
- 直接管理用户配置

### 当前原型迁移来源
- `record_to_review_prototype.py`

---

## 五、可选扩展服务

## 6. `integration_service`
### 作用
统一管理第三方来源接入。

### 适合放什么
- Binance Connector
- Coinglass Connector
- GMGN Connector（若后续可行）

### 为什么它是可选的
小型实现里，也可以先把 Connector 直接放在 `market_data_service` 下。  
如果后面数据源变多，再单独抽离。

---

## 7. `skill_entry_service`
### 作用
负责：
- 接住来自 Skill / CLI / API 的调用
- 把自然输入转成标准业务输入
- 调用下层 service

### 适合放什么
- 输入标准化
- 调用分发
- 输出装配

### 当前原型迁移来源
- `xinbi_cli.py`
- `xinbi_live.py` 中部分输入归一化逻辑

---

## 六、推荐的模块关系
如果用一句话概括关系：

### `market_data_service`
提供：
- 市场快照

### `risk_check_service`
消费：
- 市场快照 + 用户计划

### `alert_service`
消费：
- 新币事件 + 市场快照

### `record_service`
消费：
- 用户计划 + 风控结果 + 市场快照

### `review_service`
消费：
- 已记录交易 + 用户结果

这样职责就会比较干净。

---

## 七、当前原型迁移建议
正式替换时，建议按下面方式迁移：

### 第一步
先把 `binance_connector_prototype.py` 迁到：
- `market_data_service`

### 第二步
把 `xinbi_live.py` 拆成：
- `market_data_service`
- `risk_check_service`

### 第三步
把 `xinbi_cli.py` 的调用边界迁到：
- `skill_entry_service`

### 第四步
把提醒原型迁到：
- `alert_service`

### 第五步
把记录 / 复盘原型迁到：
- `record_service`
- `review_service`

---

## 八、当前最重要的实现建议
现在最值得先正式化的服务层，不是全部一起做，
而是按优先级先做：

### P0
- `market_data_service`
- `risk_check_service`

### P1
- `record_service`
- `review_service`

### P2
- `alert_service`

### P3
- `integration_service`
- `skill_entry_service`

这个顺序的原因是：
- 市场快照和风控是当前主骨架
- 记录与复盘是闭环支撑
- 提醒入口可以在后面迁
- 更复杂的统一入口和外部接入治理最后再抽象

---

## 九、当前阶段一句话结论
当前最合适的做法，不是继续增加新的脚本，
而是：

> **以 `market_data_service` 和 `risk_check_service` 为第一批正式服务层，把已经跑通的 Binance + live 风控原型先稳定下来，再把记录、复盘、提醒逐步迁进去。**

这会是从“原型系统”走向“正式 MVP 服务结构”的最稳路径。
