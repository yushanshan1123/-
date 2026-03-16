# USER_ALERT_CONFIG_SCHEMA.md

## 项目名称
新币合约交易冷静器 2.1

## Day 4 目标
定义用户提醒配置（`UserAlertConfig`）的统一结构，让系统知道：

- 哪个用户要不要接收提醒
- 要接收哪些提醒节点
- 是否附带价格
- 是否附带市场结构信息
- 提醒应该发到哪里

这份文档解决的问题是：

> **当新币公告来了，系统如何判断“该不该提醒这个用户，以及怎么提醒”。**

---

## 一、为什么必须有 UserAlertConfig
如果没有用户提醒配置，后面会有几个问题：

1. 系统不知道谁开启了提醒
2. 系统不知道按哪个时区提醒
3. 系统不知道提醒内容要不要附带价格和市场数据
4. 系统不知道用户只想看哪些币或哪些市场类型

所以提醒系统必须以 `UserAlertConfig` 为基础。

---

## 二、UserAlertConfig 顶层结构
建议统一对象如下：

```json
{
  "userId": "telegram:6482140148",
  "alertsEnabled": true,
  "timezone": "Asia/Shanghai",
  "alertAnnouncement": true,
  "alertPre5m": false,
  "alertLive": false,
  "alertPost5m": false,
  "includePrice": true,
  "includeMarketData": true,
  "includeRiskCheckEntry": true,
  "includeQuickReviewEntry": true,
  "watchMode": "all",
  "watchPairs": [],
  "watchMarketType": "all",
  "deliveryChannel": "telegram",
  "deliveryTarget": "telegram:6482140148",
  "notes": "",
  "createdAt": "2026-03-11T16:00:00Z",
  "updatedAt": "2026-03-11T16:00:00Z"
}
```

---

## 三、字段说明

---

## A. 用户身份字段

### 1. userId
- 类型：string
- 含义：用户唯一标识
- 示例：`telegram:6482140148`
- 必需性：P0
- 用途：
  - 配置绑定
  - 提醒发送目标查找

---

## B. 提醒总开关字段

### 2. alertsEnabled
- 类型：boolean
- 含义：是否开启提醒系统
- 必需性：P0
- 用途：
  - 如果为 `false`，后续不发送任何主动提醒

---

## C. 时间与节点字段

### 3. timezone
- 类型：string
- 含义：用户时区
- 示例：`Asia/Shanghai`
- 必需性：P0
- 用途：
  - 提醒时间换算
  - 文案展示本地时间

### 4. alertAnnouncement
- 类型：boolean
- 含义：是否接收“公告发布时提醒”
- 必需性：P0

### 5. alertPre5m
- 类型：boolean
- 含义：是否接收“上线前 5 分钟提醒”
- 必需性：P1

### 6. alertLive
- 类型：boolean
- 含义：是否接收“上线时提醒”
- 必需性：P1

### 7. alertPost5m
- 类型：boolean
- 含义：是否接收“上线后 5 分钟提醒”
- 必需性：P1

> MVP 第一版建议先只强制实现 `alertAnnouncement`，其余先保留字段。

---

## D. 内容增强字段

### 8. includePrice
- 类型：boolean
- 含义：提醒消息中是否附带当前价格
- 必需性：P0
- 用途：
  - 公告提醒是否显示价格

### 9. includeMarketData
- 类型：boolean
- 含义：提醒消息中是否附带市场结构数据
- 必需性：P0
- 用途：
  - 是否带上多空比、结构摘要等

### 10. includeRiskCheckEntry
- 类型：boolean
- 含义：提醒中是否附带“风控入口”
- 必需性：P0
- 用途：
  - 提醒后能否自然引导进入风控

### 11. includeQuickReviewEntry
- 类型：boolean
- 含义：提醒中是否附带“新币速评入口”
- 必需性：P1
- 用途：
  - 提醒后能否先看速评

---

## E. 关注范围字段

### 12. watchMode
- 类型：string
- 建议值：
  - `all`
  - `custom`
- 必需性：P0
- 用途：
  - 全部新币提醒还是自定义提醒

### 13. watchPairs
- 类型：array
- 含义：用户指定关注的交易对列表
- 示例：`["LOBSTERUSDT", "ABCUSDT"]`
- 必需性：P1
- 用途：
  - 当 `watchMode = custom` 时生效

### 14. watchMarketType
- 类型：string
- 建议值：
  - `all`
  - `spot`
  - `futures`
- 必需性：P1
- 用途：
  - 用户只关心现货还是合约

---

## F. 发送目标字段

### 15. deliveryChannel
- 类型：string
- 含义：提醒发到哪个渠道
- 示例：`telegram`
- 必需性：P0

### 16. deliveryTarget
- 类型：string
- 含义：提醒具体发到哪里
- 示例：`telegram:6482140148`
- 必需性：P0

---

## G. 备注与时间字段

### 17. notes
- 类型：string
- 含义：用户补充偏好备注
- 必需性：P2

### 18. createdAt
- 类型：string
- 含义：配置创建时间
- 必需性：P0

### 19. updatedAt
- 类型：string
- 含义：配置更新时间
- 必需性：P0

---

## 四、MVP 第一版最小字段集
第一版先保证最小可运行配置。

```json
{
  "userId": "telegram:6482140148",
  "alertsEnabled": true,
  "timezone": "Asia/Shanghai",
  "alertAnnouncement": true,
  "includePrice": true,
  "includeMarketData": true,
  "includeRiskCheckEntry": true,
  "watchMode": "all",
  "deliveryChannel": "telegram",
  "deliveryTarget": "telegram:6482140148",
  "createdAt": "2026-03-11T16:00:00Z",
  "updatedAt": "2026-03-11T16:00:00Z"
}
```

---

## 五、配置缺失时的处理规则

### 情况 1：没有配置
系统不主动提醒，先引导用户完成订阅配置。

### 情况 2：配置存在，但 `alertsEnabled = false`
系统不发提醒。

### 情况 3：没有 timezone
系统不能做依赖用户本地时间表达的提醒，必须先补时区。

### 情况 4：没有 deliveryTarget
系统不能发提醒，必须先补目标。

---

## 六、Day 4（配置部分）完成标志
满足以下条件，即视为 `UserAlertConfig` 设计完成：

- 已定义清楚最小字段集
- 已定义提醒节点字段
- 已定义内容增强字段
- 已定义发送目标字段
- 已定义缺失配置时的处理规则

---

## 七、下一步
与 `LISTING_EVENT_SCHEMA.md` 一起配合使用，进入提醒事件流设计。
