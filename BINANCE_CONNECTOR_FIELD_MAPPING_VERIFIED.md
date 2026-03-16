# BINANCE_CONNECTOR_FIELD_MAPPING_VERIFIED.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于记录：

> **Binance 主骨架中，哪些字段已经完成了第一轮真实可行性验证，以及它们应该如何映射进 Connector 与 `MarketSnapshot`。**

这不是概念设计文档，重点是把“已经验证能拿到的数据”整理成可执行对照表。

---

## 一、当前结论
目前已完成第一轮真实验证的 Binance 主骨架字段包括：

- `price`
- `change24h`
- `longShortRatio`
- `openInterest`
- `topTraderLongShortRatio`

验证方式：
- 直接请求 Binance Futures 公共接口
- 使用 `BTCUSDT` 进行样例验证
- 返回状态均为 `200`

这说明：

> **Binance 主骨架可以先基于公共接口接入，不需要先依赖私有授权。**

---

## 二、已验证接口总览

| 目标字段 | Binance 接口 | 是否验证成功 | 备注 |
|---|---|---|---|
| `price` | `/fapi/v1/ticker/24hr` | 是 | 从 `lastPrice` 映射 |
| `change24h` | `/fapi/v1/ticker/24hr` | 是 | 从 `priceChangePercent` 映射 |
| `longShortRatio` | `/futures/data/globalLongShortAccountRatio` | 是 | 从返回 `longShortRatio` 映射 |
| `openInterest` | `/fapi/v1/openInterest` | 是 | 从返回 `openInterest` 映射 |
| `topTraderLongShortRatio` | `/futures/data/topLongShortPositionRatio` | 是 | 从返回 `longShortRatio` 映射 |

---

## 三、字段逐项映射

## 1. `price`
### 已验证接口
`GET /fapi/v1/ticker/24hr?symbol={pair}`

### 已验证样例
`/fapi/v1/ticker/24hr?symbol=BTCUSDT`

### 已验证返回字段
```json
{
  "lastPrice": "70544.80"
}
```

### Connector 映射
```json
"price": 70544.80
```

### `MarketSnapshot` 映射
```json
"price": 70544.80
```

### 备注
- 原始值为字符串
- Connector 层必须转成 `number`

---

## 2. `change24h`
### 已验证接口
`GET /fapi/v1/ticker/24hr?symbol={pair}`

### 已验证样例
`/fapi/v1/ticker/24hr?symbol=BTCUSDT`

### 已验证返回字段
```json
{
  "priceChangePercent": "-0.283"
}
```

### Connector 映射
```json
"change24h": -0.283
```

### `MarketSnapshot` 映射
```json
"change24h": -0.283
```

### 备注
- 原始值为字符串
- Connector 层必须转成 `number`
- 不要保留百分号字符串格式

---

## 3. `longShortRatio`
### 已验证接口
`GET /futures/data/globalLongShortAccountRatio?symbol={pair}&period=5m&limit=1`

### 已验证样例
`/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1`

### 已验证返回字段
```json
[
  {
    "longShortRatio": "1.1349",
    "timestamp": 1773250500000
  }
]
```

### Connector 映射
```json
"longShortRatio": 1.1349
```

### `MarketSnapshot` 映射
```json
"longShortRatio": 1.1349
```

### 备注
- 原始结果为数组
- 第一版可先取 `limit=1` 的最新值
- 原始值为字符串，需转成 `number`

---

## 4. `openInterest`
### 已验证接口
`GET /fapi/v1/openInterest?symbol={pair}`

### 已验证样例
`/fapi/v1/openInterest?symbol=BTCUSDT`

### 已验证返回字段
```json
{
  "openInterest": "82994.727",
  "time": 1773250734947
}
```

### Connector 映射
```json
"openInterest": 82994.727
```

### `MarketSnapshot` 映射
```json
"openInterest": 82994.727
```

### 备注
- 原始值为字符串
- Connector 层必须转成 `number`

---

## 5. `topTraderLongShortRatio`
### 已验证接口
`GET /futures/data/topLongShortPositionRatio?symbol={pair}&period=5m&limit=1`

### 已验证样例
`/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=1`

### 已验证返回字段
```json
[
  {
    "longShortRatio": "1.0074",
    "timestamp": 1773250500000
  }
]
```

### Connector 映射
```json
"topTraderLongShortRatio": 1.0074
```

### `MarketSnapshot` 映射
```json
"topTraderLongShortRatio": 1.0074
```

### 备注
- 原始结果为数组
- 第一版可先取 `limit=1` 的最新值
- 原始字段名虽然也叫 `longShortRatio`，但在内部必须映射为 `topTraderLongShortRatio`

---

## 四、建议的 Connector 最小输出
结合当前已验证结果，Connector 第一版最小输出可以固定为：

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

---

## 五、建议的 `MarketSnapshot` 最小输出
映射后建议固定为：

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

## 六、落地时的实现注意点

### 1. 所有数值字段都要转成 `number`
不能把 Binance 返回的字符串原样透传。

### 2. 数组型接口先取最新一条
对于：
- `globalLongShortAccountRatio`
- `topLongShortPositionRatio`

第一版可先采用：
- `limit=1`
- 取数组第一条

### 3. 时间统一由后端生成或统一转换
不要混用不同接口的原始时间字段做最终快照时间。

### 4. `topTraderLongShortRatio` 必须改内部名
虽然上游返回也叫 `longShortRatio`，但内部绝不能和普通账户多空比混淆。

---

## 七、当前阶段的结论
当前已经可以确认：

- Binance 主骨架字段可通过公共接口获取
- 核心字段具备明确上游来源
- 字段映射逻辑已能固定
- 下一步可以进入真实 Connector 拼装阶段

这意味着当前最重要的工作，已经不再是“论证 Binance 是否可接”，而是：

> **按这份对照表，把已验证字段真正接进 Connector 与 `MarketSnapshot`。**
