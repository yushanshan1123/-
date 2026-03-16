# DELIVERY_FACADE_TRANSITION_NOTES.md

## 当前新增内容
已新增：
- `delivery_facade.py`
- `validate_delivery_facade.py`

## 这层的定位
这是一层正式命名的 delivery facade 过渡层。

它的作用是：
- 对发送接口提供稳定 facade 名称
- 当前内部仍回落到 `delivery_facade_mock.py`
- 未来真实发送接入时，优先替换这层内部实现

## 当前价值
这意味着当前项目已经不必让上层直接依赖：
- `delivery_facade_mock.py`

而可以统一依赖：
- `delivery_facade.py`

## 当前边界
目前它仍然没有：
- 真正 `message.send` 接入
- 真实 provider message id 映射
- 真实失败处理与重试

所以它应被理解为：

> **从 mock facade 继续推进到正式 facade 名称的过渡层。**
