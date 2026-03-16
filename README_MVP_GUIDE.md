# README_MVP_GUIDE.md

## 项目名称
新币合约交易冷静器 2.1

## 文档包说明
这是一套围绕 **新币公告提醒 → 开仓前风险检查 → 交易计划记录 → 后续复盘** 设计的 MVP 文档包。

它的目标不是一次性把所有功能都做完，而是先定义出一个 **最小可落地闭环**：

> 发现 Binance 新币公告 → 发送提醒 → 用户进入风控 → 系统读取真实市场数据 → 输出结构化风险检查 → 用户记录这笔计划 → 后续可复盘

这套文档包适合：
- 自己梳理产品
- 给别人讲项目
- 后续继续推进实现
- 为参赛或展示做内容准备

---

## 一、项目当前阶段
当前阶段是：

### MVP 第一版设计阶段
第一版先围绕 Binance 公开数据建立主骨架，优先实现：
- 新币公告识别
- 公告提醒
- 基础市场数据接入
- 开仓前风险检查
- 交易计划记录
- 轻量复盘入口

### 第一版明确不做
- GMGN.ai 聪明钱层（延后）
- Coinglass 清算热力（延后）
- 私有账户授权（延后）
- 自动下单（不做）
- 复杂复盘看板（延后）

---

## 二、文档总目录

### 1. `MVP_SCOPE.md`
**作用：** 锁定 MVP 第一版范围。

你先看这个文件，先弄清楚：
- 第一版要做什么
- 第一版不做什么
- 成功标准是什么

---

### 2. `BINANCE_FIELDS_MAP.md`
**作用：** 梳理 MVP 第一版需要的 Binance 字段。

主要回答：
- 要哪些字段
- 字段属于哪类数据
- 每个字段在 Skill 里的用途

---

### 3. `MARKET_SNAPSHOT_SCHEMA.md`
**作用：** 定义统一市场快照对象。

主要回答：
- 后端统一数据结构长什么样
- Skill 以后应该读什么对象
- 数据缺失时如何降级

---

### 4. `USER_ALERT_CONFIG_SCHEMA.md`
**作用：** 定义用户提醒配置结构。

主要回答：
- 提醒谁
- 提醒哪些节点
- 是否附带价格 / 市场结构
- 提醒发到哪里

---

### 5. `LISTING_EVENT_SCHEMA.md`
**作用：** 定义新币事件对象。

主要回答：
- 一个新币公告在系统内部怎么存
- 上线时间怎么管理
- 提醒状态怎么追踪

---

### 6. `ALERT_MESSAGE_TEMPLATE.md`
**作用：** 定义提醒消息模板。

主要回答：
- 公告提醒怎么写
- 带价格版怎么写
- 用户收到提醒后怎么分流到速评 / 风控

---

### 7. `RISK_CHECK_TEMPLATE.md`
**作用：** 定义开仓前风险检查模板。

主要回答：
- 用户要输入什么
- 系统要看什么数据
- 风险等级怎么给
- 风控结果怎么输出

---

### 8. `TRADE_REVIEW_RECORD_SCHEMA.md`
**作用：** 定义交易计划记录结构。

主要回答：
- 用户说“记录这笔计划”时，到底存什么
- 市场快照怎么留痕

---

### 9. `RECORD_AND_REVIEW_FLOW.md`
**作用：** 定义记录与复盘流程。

主要回答：
- 风控结束后如何进入记录
- 后续如何基于记录做轻量复盘

---

## 三、推荐阅读顺序

### 方案 A：产品理解顺序
适合你自己快速看懂整套产品逻辑。

1. `MVP_SCOPE.md`
2. `USER_ALERT_CONFIG_SCHEMA.md`
3. `LISTING_EVENT_SCHEMA.md`
4. `ALERT_MESSAGE_TEMPLATE.md`
5. `RISK_CHECK_TEMPLATE.md`
6. `RECORD_AND_REVIEW_FLOW.md`

---

### 方案 B：数据 / 后端顺序
适合后面继续落地或对接实现。

1. `MVP_SCOPE.md`
2. `BINANCE_FIELDS_MAP.md`
3. `MARKET_SNAPSHOT_SCHEMA.md`
4. `USER_ALERT_CONFIG_SCHEMA.md`
5. `LISTING_EVENT_SCHEMA.md`
6. `TRADE_REVIEW_RECORD_SCHEMA.md`

---

### 方案 C：完整闭环顺序
适合系统性完整阅读。

1. `MVP_SCOPE.md`
2. `BINANCE_FIELDS_MAP.md`
3. `MARKET_SNAPSHOT_SCHEMA.md`
4. `USER_ALERT_CONFIG_SCHEMA.md`
5. `LISTING_EVENT_SCHEMA.md`
6. `ALERT_MESSAGE_TEMPLATE.md`
7. `RISK_CHECK_TEMPLATE.md`
8. `TRADE_REVIEW_RECORD_SCHEMA.md`
9. `RECORD_AND_REVIEW_FLOW.md`

---

## 四、文档之间的逻辑链路
整个文档包的逻辑是：

### 先定边界
`MVP_SCOPE.md`

↓

### 再定数据来源和字段
`BINANCE_FIELDS_MAP.md`

↓

### 再统一成市场快照对象
`MARKET_SNAPSHOT_SCHEMA.md`

↓

### 再定义用户与事件
`USER_ALERT_CONFIG_SCHEMA.md`
`LISTING_EVENT_SCHEMA.md`

↓

### 再定义提醒如何发出
`ALERT_MESSAGE_TEMPLATE.md`

↓

### 再定义风控如何判断
`RISK_CHECK_TEMPLATE.md`

↓

### 最后形成记录与复盘闭环
`TRADE_REVIEW_RECORD_SCHEMA.md`
`RECORD_AND_REVIEW_FLOW.md`

---

## 五、当前 MVP 的核心闭环
当前这套文档定义的最小闭环是：

**公告识别 → 公告提醒 → 用户风控 → 系统判断 → 用户记录 → 后续复盘**

如果这一条链可以跑通，就视为 MVP 第一版成立。

---

## 六、这套文档包现在最适合怎么用

### 用法 1：你自己梳理产品
按“产品理解顺序”看。

### 用法 2：后续继续推进实现
按“数据 / 后端顺序”看。

### 用法 3：给别人介绍项目
优先讲这 4 份：
- `MVP_SCOPE.md`
- `ALERT_MESSAGE_TEMPLATE.md`
- `RISK_CHECK_TEMPLATE.md`
- `RECORD_AND_REVIEW_FLOW.md`

因为这四份最容易让人理解你的项目价值。

---

## 七、下一步建议
当前文档包已经足够支撑两条后续路线：

### 路线 A：继续落地
往实现侧推进，例如：
- 真正接 Binance 数据
- 真正生成 ListingEvent
- 真正发出公告提醒
- 真正运行风控检查

### 路线 B：准备展示 / 参赛
把这套文档包压缩成：
- 项目说明
- 图文展示
- 参赛提交文案

---

## 八、当前阶段一句话总结
这套文档包的意义，不是记录一个点子，
而是把 **新币合约交易冷静器 2.1** 从“想法”推进成了一个：

> **有边界、有数据骨架、有事件流、有提醒逻辑、有风控模板、有记录闭环的 MVP 产品蓝图。**
