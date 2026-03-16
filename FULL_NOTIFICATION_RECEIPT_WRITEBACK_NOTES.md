# FULL_NOTIFICATION_RECEIPT_WRITEBACK_NOTES.md

## 当前新增内容
已新增/更新：
- `full_notification_demo.py`
- `validate_full_notification_demo.py`

## 这次补了什么
这次给 full notification demo 增加了可选的：
- `receiptMode = delivered`
- `receiptMode = failed`

也就是说，整链 demo 现在已经具备“尝试继续演示发送后回执回写”的入口。

## 当前行为
### 默认
不传 `receiptMode`：
- 仍只演示到 delivery result

### 传 `receiptMode`
- 会尝试对 delivery result 对应的记录继续做回写
- 当前若 delivery result 仍是 `mock_sent`，会返回：
  - `RECEIPT_NOT_APPLICABLE`

## 为什么这也有价值
因为它把“整链 demo”与“回写 demo”的关系也钉住了：
- 不是所有 deliveryStatus 都适合做 receipt writeback
- `mock_sent` 当前只是 mock 终态，不是 provider sent 状态

## 当前一句话结论

> **full notification demo 已具备 receipt writeback 入口，但当前默认 mock 发送路径下，receipt writeback 仍不会真正生效。**
