# PROVIDER_DELIVERY_FAILURE_DEMO_NOTES.md

## 当前新增内容
已新增：
- `provider_delivery_failure_demo.py`
- `validate_provider_delivery_failure_demo.py`

## 这层的定位
这是一个伪 provider 失败回执 / 回写演示脚本。

它的作用是：
- 先构造一条 `sent` 发送记录
- 再模拟 provider 失败回执把状态更新成 `failed`
- 演示 providerMessageId 在失败回写时继续保留

## 当前价值
这意味着发送链现在除了有：
- `sent -> delivered` 回写 demo

也开始有：
- `sent -> failed` 回写 demo

## 当前边界
目前它仍然不是真实 provider webhook。
所以它应被理解为：

> **真实失败回执接入前的最小本地失败回写 demo。**
