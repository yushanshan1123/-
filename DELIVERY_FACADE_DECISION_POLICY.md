# DELIVERY_FACADE_DECISION_POLICY.md

## 当前目标
这份文档用于固定：

> **`delivery_facade.py` 当前如何在 real adapter 与 mock fallback 之间做决策。**

---

## 一、当前决策规则
### 默认路径
如果未显式开启：
- `XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY=1`

则：
- 直接走 mock delivery

### real adapter 路径
如果显式开启：
- `XINBI_ENABLE_OPENCLAW_MESSAGE_DELIVERY=1`

则：
- 先走 `openclaw_message_delivery_adapter.py`

### fallback 规则
当前仅当 real adapter 返回：
- `error = NOT_CONFIGURED`

时允许回退到 mock。

当前**不**对以下错误做 fallback：
- `INVALID_DELIVERY_PAYLOAD`

因为这类错误属于输入本身有问题，不应通过 mock 掩盖。

---

## 二、为什么这样定
这样做的好处是：
- 默认行为稳定，仍可继续本地演示
- real adapter 开关打开后，可以开始测试真实路径
- adapter 未配置时不会把整条链直接打死
- 输入错误不会被 mock 掩盖

---

## 三、当前一句话结论

> **当前 facade 策略是：默认 mock；显式启用 real adapter 时先走 real；仅在 `NOT_CONFIGURED` 时回退 mock。**
