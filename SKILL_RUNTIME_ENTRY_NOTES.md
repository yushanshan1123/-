# SKILL_RUNTIME_ENTRY_NOTES.md

## 当前新增内容
已新增：
- `services/skill_runtime_service/service.py`

## 这层的定位
这不是替代业务 service，
而是给未来正式 Skill / 后端调用准备的一层轻适配：

- 接统一的 `action`
- 接统一的 `payload`
- 接统一的 `context`
- 返回统一 envelope：`ok / runtimeMeta / data`

## 当前已支持 action
- `snapshot`
- `risk_check`
- `alert_to_risk`
- `alert_to_review`
- `risk_to_record`
- `record_to_review`

## 当前价值
这层让项目不再只有 CLI 风格入口，
而是开始具备更像“Skill runtime 调用协议”的统一入口骨架。

## 当前边界
它目前仍然是本地代码内部分发层，不代表：
- 已有正式 HTTP API
- 已有正式调度系统
- 已有正式消息回写

所以应把它理解为：

> **从 `skill_entry_service` 再往上抽一层，更接近未来正式 runtime 的入口骨架。**
