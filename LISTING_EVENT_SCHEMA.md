# LISTING_EVENT_SCHEMA.md

## 项目名称
新币合约交易冷静器 2.1

## Day 4 目标
定义新币事件（`ListingEvent`）的统一结构，让系统能把 Binance 新币公告转成一个可调度、可提醒、可追踪的事件对象。

这份文档解决的问题是：

> **当系统发现一个新币公告后，它到底该把这件事存成什么样，后面才好做提醒和状态管理。**

---

## 一、为什么必须有 ListingEvent
如果没有 `ListingEvent`，会出现这些问题：

1. 公告看完就丢，后面没法做提醒调度
2. 无法区分同一个币的不同上线事件
3. 不知道哪些提醒发过了，哪些没发
4. 后续无法做事件回溯和日志记录

所以新币公告必须转成一个系统内部的“事件对象”。

---

## 二、ListingEvent 顶层结构
建议统一对象如下：

```json
{
  "eventId": "listing_LOBSTER_20260311_1000",
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "marketType": "spot",
  "announcementTime": "2026-03-11T08:00:00Z",
  "listingTime": "2026-03-11T10:00:00Z",
  "sourceUrl": "https://...",
  "eventStatus": "scheduled",
  "reminderAnnouncementSent": true,
  "reminderPre5mSent": false,
  "reminderLiveSent": false,
  "reminderPost5mSent": false,
  "createdAt": "2026-03-11T08:00:05Z",
  "updatedAt": "2026-03-11T08:00:05Z"
}
```

---

## 三、字段说明

---

## A. 事件标识字段

### 1. eventId
- 类型：string
- 含义：事件唯一 ID
- 示例：`listing_LOBSTER_20260311_1000`
- 必需性：P0
- 用途：
  - 唯一标识一个新币事件
  - 防止重复创建
  - 提醒状态关联

### 生成建议
可以用：
- 事件类型 + symbol + listingTime

---

## B. 标的识别字段

### 2. symbol
- 类型：string
- 含义：币种代码
- 示例：`LOBSTER`
- 必需性：P0

### 3. pair
- 类型：string
- 含义：交易对
- 示例：`LOBSTERUSDT`
- 必需性：P0

### 4. marketType
- 类型：string
- 建议值：
  - `spot`
  - `futures`
- 必需性：P1
- 用途：
  - 区分事件属于现货还是合约

---

## C. 事件时间字段

### 5. announcementTime
- 类型：string
- 格式：ISO 8601 UTC
- 含义：公告发布时间
- 必需性：P0
- 用途：
  - 公告提醒时间

### 6. listingTime
- 类型：string
- 格式：ISO 8601 UTC
- 含义：上线时间
- 必需性：P0
- 用途：
  - 上线前 5 分钟提醒
  - 上线时提醒
  - 上线后 5 分钟提醒

---

## D. 来源字段

### 7. sourceUrl
- 类型：string
- 含义：原始公告链接
- 必需性：P0
- 用途：
  - 提醒消息回溯
  - 便于人工核对

---

## E. 事件状态字段

### 8. eventStatus
- 类型：string
- 建议值：
  - `new`
  - `scheduled`
  - `live`
  - `completed`
  - `cancelled`
- 必需性：P0
- 用途：
  - 标记当前事件所处阶段

---

## F. 提醒状态字段
这些字段决定后端知道“发过没”。

### 9. reminderAnnouncementSent
- 类型：boolean
- 含义：是否已发送公告提醒
- 必需性：P0

### 10. reminderPre5mSent
- 类型：boolean
- 含义：是否已发送上线前 5 分钟提醒
- 必需性：P1

### 11. reminderLiveSent
- 类型：boolean
- 含义：是否已发送上线提醒
- 必需性：P1

### 12. reminderPost5mSent
- 类型：boolean
- 含义：是否已发送上线后 5 分钟提醒
- 必需性：P1

> MVP 第一版建议先强制实现 `reminderAnnouncementSent`，其余字段先预留。

---

## G. 系统时间字段

### 13. createdAt
- 类型：string
- 含义：事件创建时间
- 必需性：P0

### 14. updatedAt
- 类型：string
- 含义：事件更新时间
- 必需性：P0

---

## 四、MVP 第一版最小字段集
第一版只要求先支持最小闭环。

```json
{
  "eventId": "listing_LOBSTER_20260311_1000",
  "symbol": "LOBSTER",
  "pair": "LOBSTERUSDT",
  "announcementTime": "2026-03-11T08:00:00Z",
  "listingTime": "2026-03-11T10:00:00Z",
  "sourceUrl": "https://...",
  "eventStatus": "scheduled",
  "reminderAnnouncementSent": false,
  "createdAt": "2026-03-11T08:00:05Z",
  "updatedAt": "2026-03-11T08:00:05Z"
}
```

---

## 五、事件生命周期建议
这个对象后面会经历一个生命周期。

### 1. new
刚从公告解析出来

### 2. scheduled
已建事件，可进入提醒调度

### 3. live
已到上线时刻

### 4. completed
提醒已完成，事件收尾

### 5. cancelled
若公告有变更或撤销

---

## 六、第一版提醒调度逻辑（与事件状态相关）

### MVP 第一版先只做：公告提醒
所以最小逻辑可以是：

1. 创建 ListingEvent
2. `reminderAnnouncementSent = false`
3. 调度器检查到该事件还没发公告提醒
4. 发送提醒
5. 更新：`reminderAnnouncementSent = true`
6. `eventStatus = scheduled`

后续增强版再加：
- pre5m
- live
- post5m

---

## 七、事件去重建议
同一个币、同一个交易对、同一个上线时间，不应该重复建事件。

### 建议去重键
- symbol
- pair
- listingTime

### 最佳实践
后端在创建事件前先检查是否已有相同 eventId。

---

## 八、异常情况处理

### 情况 1：公告解析成功，但 listingTime 缺失
处理建议：
- 仍可创建事件
- 但标记为部分事件
- 只能发公告提醒，不能做后续时间节点提醒

### 情况 2：同一事件重复抓到
处理建议：
- 更新现有事件，不重复创建

### 情况 3：公告被修改
处理建议：
- 更新 listingTime
- 重算后续提醒任务
- 更新 `updatedAt`

---

## 九、ListingEvent 与其他对象的关系

### 与 UserAlertConfig 的关系
- ListingEvent 决定“发生了什么”
- UserAlertConfig 决定“要不要提醒谁”

### 与 MarketSnapshot 的关系
- ListingEvent 提供 `pair`
- MarketSnapshot 提供当前市场状态

### 与提醒消息的关系
提醒消息是：
- `ListingEvent` + `UserAlertConfig` + `MarketSnapshot`
一起生成的。

---

## 十、Day 4（事件流部分）完成标志
满足以下条件，即视为 `ListingEvent` 设计完成：

- 已定义事件最小字段集
- 已定义提醒状态字段
- 已定义事件生命周期
- 已定义去重逻辑
- 已定义缺失时间和重复事件的处理规则

---

## 十一、下一步
Day 5 进入：

**公告提醒模板与自动提醒发送流程设计**
