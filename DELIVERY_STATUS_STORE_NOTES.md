# DELIVERY_STATUS_STORE_NOTES.md

## 当前新增内容
已新增：
- `delivery_status_store_mock.py`
- `delivery_status_records.json`

## 这层的定位
这不是正式发送状态数据库，
而是一个本地发送状态记录 mock。

它的作用是：
- 接住 delivery facade 的发送结果
- 把最小发送状态留到本地文件
- 提前验证“发送后留痕”这一步的结构

## 当前已记录的关键字段
- `deliveryStatus`
- `deliveryChannel`
- `targetUserId`
- `mockMessageId`
- `sentAt`
- `requestId`
- `traceId`

## 当前边界
目前没有：
- 真正数据库
- 真正状态更新
- 真正失败重试状态流转

所以它应被理解为：

> **真实发送状态记录前一层的本地 mock。**
