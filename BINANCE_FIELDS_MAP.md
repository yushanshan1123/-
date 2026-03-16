# BINANCE_FIELDS_MAP.md

## 项目名称
新币合约交易冷静器 2.1

## Day 2 目标
确认 MVP 第一版所需的 Binance 数据字段，以及这些字段分别应该从哪一类 Binance 官方公开数据入口获取。

这份文档的目标不是一次写死所有接口细节，而是先把：

- **需要哪些字段**
- **这些字段属于哪类 Binance 数据**
- **它们在 Skill 里有什么用**

三件事梳理清楚。

---

## 一、Day 2 的核心原则

### 原则 1：第一版只用 Binance 公开市场数据
不依赖：
- 用户账户
- 用户资产
- 用户私有仓位
- 用户订单权限

### 原则 2：先保证主骨架字段齐全
Day 2 的重点不是追求所有细节，而是把 MVP 必须字段先对齐。

### 原则 3：先字段映射，再细化接口
先知道要什么，再决定具体调用顺序和适配器实现。

---

## 二、MVP 第一版必须字段总表

| 统一字段名 | 中文含义 | Binance 数据类型 | MVP 必需性 | Skill 用途 |
|---|---|---|---|---|
| symbol | 币种代码 | 公告 / 行情 | 必须 | 提醒、速评、风控 |
| pair | 交易对 | 公告 / 行情 | 必须 | 提醒、速评、风控 |
| announcementTime | 公告发布时间 | 公告 | 必须 | 提醒事件 |
| listingTime | 上线时间 | 公告 | 必须 | 提醒调度 |
| sourceUrl | 公告链接 | 公告 | 必须 | 消息提醒、跳转 |
| price | 当前价格 | 行情 | 必须 | 速评、风控 |
| change24h | 24h 涨跌幅 | 行情 | 必须 | 速评、风控 |
| high24h | 24h 最高价 | 行情 | 建议 | 波动参考 |
| low24h | 24h 最低价 | 行情 | 建议 | 波动参考 |
| volume24h | 24h 成交量 | 行情 | 建议 | 热度参考 |
| longShortRatio | 多空持仓人数比 | 合约公开数据 | 必须 | 风控 |
| openInterest | 合约持仓量（OI） | 合约公开数据 | 必须 | 风控 |
| topTraderLongShortRatio | 大户持仓多空比 | 合约公开数据 | 必须 | 风控 |
| snapshotTime | 快照时间 | 后端生成 / 接口时间 | 必须 | 记录与复盘 |
| sourceBinanceStatus | Binance 数据状态 | 后端生成 | 必须 | 降级处理 |

---

## 三、字段分层映射

---

## A. 公告事件层字段
这些字段用于：
- 新币提醒
- ListingEvent 事件流
- 提醒调度

### 1. symbol
- 含义：币种代码，例如 `LOBSTER`
- 来源：Binance 新币公告
- 用途：
  - 提醒标题
  - 风控标的识别
  - 记录交易计划

### 2. pair
- 含义：交易对，例如 `LOBSTERUSDT`
- 来源：Binance 公告 / 行情
- 用途：
  - 市场数据读取主键
  - 风控分析目标

### 3. announcementTime
- 含义：公告发布时间
- 来源：Binance 公告
- 用途：
  - 判断公告提醒何时触发

### 4. listingTime
- 含义：上线时间
- 来源：Binance 公告
- 用途：
  - 上线前 5 分钟提醒
  - 上线时提醒
  - 上线后 5 分钟提醒

### 5. sourceUrl
- 含义：公告链接
- 来源：Binance 公告
- 用途：
  - 提醒消息里附带原始来源
  - 方便回溯和核对

---

## B. 行情层字段
这些字段用于：
- 新币速评
- 开仓前风控
- 提醒中附带价格信息

### 6. price
- 含义：当前价格
- 来源：Binance 市场行情
- 用途：
  - 提醒时显示当前价格
  - 风控时判断用户是不是在追高 / 追空
  - 记录开仓时刻价格

### 7. change24h
- 含义：24h 涨跌幅
- 来源：Binance 市场行情
- 用途：
  - 判断当前是否处在高热度状态
  - 提醒时快速显示市场热度

### 8. high24h
- 含义：24h 最高价
- 来源：Binance 市场行情
- 用途：
  - 判断当前价格是否接近极端位置
- 第一版要求：建议保留，但不是风控第一优先字段

### 9. low24h
- 含义：24h 最低价
- 来源：Binance 市场行情
- 用途：
  - 判断波动范围
- 第一版要求：建议保留

### 10. volume24h
- 含义：24h 成交量
- 来源：Binance 市场行情
- 用途：
  - 辅助判断热度是否有量支撑
- 第一版要求：建议保留，但可晚于 price / change24h 落地

---

## C. 合约结构层字段
这些字段是 MVP 风控的核心。

### 11. longShortRatio
- 含义：多空持仓人数比
- 来源：Binance 合约公开数据
- 用途：
  - 判断当前散户/普通账户更偏多还是偏空
  - 判断市场情绪是否拥挤

### 12. openInterest
- 含义：合约持仓量（Open Interest）
- 来源：Binance 合约公开数据
- 用途：
  - 判断市场是否在持续加仓博弈
  - 判断当前波动是否有真实仓位推动

### 13. topTraderLongShortRatio
- 含义：大户持仓多空比
- 来源：Binance 合约公开数据
- 用途：
  - 判断大资金方向
  - 判断用户计划是否与大户结构冲突

---

## D. 系统补充字段
这些字段不是 Binance 原始字段，但必须统一定义。

### 14. snapshotTime
- 含义：当前市场快照时间
- 来源：
  - 接口返回时间 或
  - 后端采集时间
- 用途：
  - 记录风控时刻
  - 后续复盘

### 15. sourceBinanceStatus
- 含义：当前 Binance 数据状态
- 取值建议：
  - `ok`
  - `partial`
  - `error`
  - `missing`
- 来源：后端生成
- 用途：
  - Skill 做降级说明
  - 告诉用户哪些判断缺数据

---

## 四、字段优先级排序

### P0：第一版必须先打通
这些字段不通，MVP 风控不成立。

- symbol
- pair
- announcementTime
- listingTime
- sourceUrl
- price
- change24h
- longShortRatio
- openInterest
- topTraderLongShortRatio
- snapshotTime
- sourceBinanceStatus

### P1：建议第一版尽量补上
- high24h
- low24h
- volume24h

### P2：后续增强
与 Binance 无关的增强层后续再接：
- fundingRate（Coinglass）
- liquidationHeatmap（Coinglass）
- smartMoneyObserved（GMGN.ai）

---

## 五、字段与功能模块对应关系

| 字段 | 提醒 | 新币速评 | 风控检查 | 交易计划记录 |
|---|---|---|---|---|
| symbol | ✓ | ✓ | ✓ | ✓ |
| pair | ✓ | ✓ | ✓ | ✓ |
| announcementTime | ✓ |  |  |  |
| listingTime | ✓ |  |  |  |
| sourceUrl | ✓ |  |  |  |
| price | ✓ | ✓ | ✓ | ✓ |
| change24h | ✓ | ✓ | ✓ | ✓ |
| high24h |  | ✓ | ✓ |  |
| low24h |  | ✓ | ✓ |  |
| volume24h |  | ✓ | ✓ |  |
| longShortRatio |  |  | ✓ | ✓ |
| openInterest |  |  | ✓ | ✓ |
| topTraderLongShortRatio |  |  | ✓ | ✓ |
| snapshotTime |  |  | ✓ | ✓ |
| sourceBinanceStatus |  | ✓ | ✓ |  |

---

## 六、第一版字段缺失时的降级规则

### 情况 1：公告字段齐全，但没有行情数据
系统仍可提醒用户，但要明确说：

> 当前未附带实时价格和市场结构数据。

### 情况 2：有价格和涨跌，但没有合约结构数据
系统可以：
- 做基础速评
- 做基础风控

但必须说明：

> 当前缺少多空结构和大户方向数据，本次判断不包含结构层分析。

### 情况 3：多空比有，但 OI / 大户多空比缺失
系统可以先给出部分风控，但要写清楚：

> 当前结构判断基于普通账户情绪，缺少大户方向或持仓量确认。

### 情况 4：Binance 数据完全不可用
系统退回 logic-only 模式，明确说明：

> 当前未接入 Binance 实时数据，以下结论仅基于用户计划和一般交易逻辑。

---

## 七、Day 2 完成标志
满足以下条件，即视为 Day 2 完成：

- 已经明确 MVP 第一版需要哪些 Binance 字段
- 已经把字段分成：公告层 / 行情层 / 合约结构层 / 系统层
- 已经明确 P0 字段列表
- 已经明确每个字段在 Skill 里的用途
- 已经明确数据缺失时怎么降级

---

## 八、下一步
Day 3 进入：

**统一 `MarketSnapshot` 数据结构设计**
