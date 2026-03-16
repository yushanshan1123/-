# DELIVERY_SERVICE_TRANSITION_NOTES.md

## 当前新增内容
已新增：
- `services/delivery_service/service.py`
- `validate_delivery_service.py`

## 这层的定位
这是一层正式发送接口的 service 占位层。

它的作用是：
- 对上层暴露统一发送入口
- 当前内部先走 `delivery_facade_mock`
- 未来替换真实发送时，只改这层内部实现

## 当前价值
这意味着提醒链现在不必直接依赖：
- `delivery_facade_mock.py`

后续如果要替换成：
- 真实 `message.send`
- 真实 Telegram / 其他渠道发送

优先替换点已经更明确了。

## 当前边界
目前仍然没有：
- 真正发送接口接入
- 渠道级失败处理
- 送达回执处理

所以它应被理解为：

> **真实发送接口替换前的 service 占位层。**
