# IMPLEMENTATION_STATUS_BOARD.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于统一追踪当前项目的实施状态，避免出现以下问题：

- 文档很多，但不知道哪些只是设计，哪些已经落地
- Skill 已更新，但数据层还没接上
- 提醒、风控、记录、复盘的完成度混在一起
- 说不清当前卡点到底在哪

核心目标是：

> **把“已完成 / 进行中 / 未开始 / 风险点”统一收束成一张可持续维护的状态板。**

---

## 一、总状态概览
当前项目状态可以概括为：

### 产品与 Skill 设计层
**已完成较多**

### 实时数据接入层
**Binance 主骨架已真实接通并被 CLI / runtime / 本地样板使用；Funding 与 Heatmap 已接入统一快照骨架但当前缺可用 Coinglass key / 稳定 endpoint；GMGN 仍被 Cloudflare/403 阻断**

### 运行模式判断
**当前已经具备真实 Binance core live 能力；Funding / Heatmap 当前处于可降级增强层骨架状态；整体仍未达到 full enhanced live / production-ready**

### MVP 产品闭环
**提醒 / 速评 / 风控 / 记录 / 复盘原型闭环已形成，核心 service 层、统一入口层、runtime 入口层、adapter 层、repository 层都已建立，记录与发送状态默认存储均已切向 SQLite；同时外部入口层已从单纯 mock 继续推进到本地 HTTP server、本地 scheduler runner、统一 external entry demo、通知整链演示与发送 service / facade 过渡层；发送结果结构、providerMessageId 兼容、queued 入口、最小 lifecycle 骨架、OpenClaw message delivery adapter 插槽、execution slot、facade 的 real/mock 决策策略、provider 成功/失败回执回写 demo，以及 full notification demo 的 receipt writeback 入口也已落下，但正式鉴权、限流、真实调度、真实发送与完整生产级 runtime / API 仍未完成**

---

## 二、状态分层定义
为了后续方便维护，建议统一使用以下四种状态：

### `done`
已完成并可直接使用

### `in_progress`
已进入明确执行阶段，但尚未真正完成

### `not_started`
尚未开始实际接入或实施

### `blocked`
已识别方向，但因外部限制、权限、稳定性等原因暂时受阻

---

## 三、状态总表

| 模块 | 状态 | 说明 |
|---|---|---|
| Skill 基础骨架 | done | 已创建并升级到 2.1 版 |
| MVP 范围定义 | done | `MVP_SCOPE.md` 已完成 |
| Binance 字段设计 | done | `BINANCE_FIELDS_MAP.md` 已完成 |
| MarketSnapshot 设计 | done | `MARKET_SNAPSHOT_SCHEMA.md` 已完成 |
| 用户提醒配置设计 | done | `USER_ALERT_CONFIG_SCHEMA.md` 已完成 |
| 新币事件结构设计 | done | `LISTING_EVENT_SCHEMA.md` 已完成 |
| 提醒模板设计 | done | `ALERT_MESSAGE_TEMPLATE.md` 已完成 |
| 风控模板设计 | done | `RISK_CHECK_TEMPLATE.md` 已完成 |
| 交易计划记录设计 | done | `TRADE_REVIEW_RECORD_SCHEMA.md` 已完成 |
| 记录与复盘流程设计 | done | `RECORD_AND_REVIEW_FLOW.md` 已完成 |
| MVP 导航文档 | done | `README_MVP_GUIDE.md` 已完成 |
| 真实接入路线图 | done | `REAL_INTEGRATION_ROADMAP.md` 已完成 |
| Binance 接入任务拆解 | done | `BINANCE_REAL_INTEGRATION_TASKLIST.md` 已完成 |
| Binance Connector 契约 | done | `BINANCE_CONNECTOR_API_CONTRACT.md` 已完成 |
| live 模式判定清单 | done | `LIVE_MODE_READINESS_CHECKLIST.md` 已完成 |
| Funding 契约 | done | `COINGLASS_FUNDING_API_CONTRACT.md` 已完成 |
| Heatmap 契约 | done | `COINGLASS_HEATMAP_API_CONTRACT.md` 已完成 |
| 提醒分流 service 化 | done | 已建立 `alert_service`，提醒 → 速评 / 风控 原型已改为薄入口 |
| 统一调用入口层 | done | 已建立 `skill_entry_service`，CLI 已统一走该层分发下层 service |
| 记录存储边界抽离 | done | 已建立 `record_repository`，service 层已与 JSON 直连解耦 |
| 存储最小回归校验 | done | 已补 `validate_record_repository_sqlite.py` 与 `STORAGE_REGRESSION_CHECKLIST.md` |
| 运行时适配层骨架 | in_progress | 已建立 `runtime_adapter_service`，并有 adapter 规划、最小校验脚本、requestId / traceId 透传骨架 |
| runtime 入口骨架 | in_progress | 已建立 `skill_runtime_service`、runtime 契约与最小验证脚本，并补了输入校验、错误包装、userId 透传、requestId / traceId 返回与常见下层错误归一 |
| 本地 HTTP 入口 mock | done | 已建立 `http_runtime_entry_mock.py` 与校验脚本，可本地模拟 HTTP body / headers → adapter → runtime |
| 本地 HTTP runtime server | in_progress | 已建立 `http_runtime_server.py` 与校验脚本，可真实接收 `POST /runtime` 并返回 JSON；但尚未补鉴权、限流、多路由与部署包装 |
| 本地 Scheduler 入口 mock | done | 已建立 `scheduler_runtime_entry_mock.py` 与校验脚本，可本地模拟 job → adapter → runtime |
| 本地 Scheduler runner | in_progress | 已建立 `scheduler_job_runner.py` 与校验脚本，可从 JSON 批量执行 job；但尚未补 cron、去重、重试、失败队列与 job 状态持久化 |
| 通知输出适配 mock | in_progress | 已建立 `notification_output_mock.py` 与校验脚本，可将 runtime 结果转成更像可发送通知的结构 |
| Telegram 输出 mock | in_progress | 已建立 `telegram_output_mock.py` 与校验脚本，可将通用通知输出转成更像 Telegram 最终发送载荷的结构 |
| 发送 facade mock | in_progress | 已建立 `delivery_facade_mock.py` 与校验脚本，可模拟渠道发送结果，并保留 mock 路径 |
| OpenClaw message delivery adapter 插槽 | in_progress | 已建立 `openclaw_message_delivery_adapter.py` 与校验脚本，当前已补 request/result/error 映射壳 |
| OpenClaw message delivery execution slot | in_progress | 已拆出 `execute_message_send_request(...)` 执行层，当前明确返回 `NOT_IMPLEMENTED`，未来真实发送优先替换此层实现 |
| 发送 formal facade 过渡层 | in_progress | 已建立 `delivery_facade.py` 与校验脚本，当前默认走 mock；显式开启 real adapter 时先走 adapter；仅在 `NOT_CONFIGURED` 时 fallback 到 mock |
| 发送 service 过渡层 | in_progress | 已建立 `services/delivery_service`，当前统一由该层承接发送调用并转发到 formal facade |
| 发送结果 schema | done | 已建立 `MESSAGE_DELIVERY_RESULT_SCHEMA.md` 与 `delivery_result_schema.py`，统一 `deliveryStatus` / `providerMessageId` / `mockMessageId` 等返回结构 |
| 发送状态 repository | in_progress | 已建立 `delivery_status_repository`，默认存储已切到 SQLite，query/store/facade 已不再直接碰 JSON |
| 发送状态 SQLite 最小回归 | done | 已补 `validate_delivery_status_sqlite.py` 与 `DELIVERY_STATUS_REGRESSION_CHECKLIST.md`，已验证 append/latest/by_request_id/list/SQLite 落地 |
| 发送状态 providerMessageId 兼容 | done | SQLite repository 已支持 `providerMessageId` 字段与向前兼容 schema 升级，最小回归已覆盖 |
| 发送 queued 入口 | in_progress | 已建立 `queue_delivery_record(payload)`，可在发送前统一落 `queued` 状态记录 |
| 发送状态 lifecycle 骨架 | in_progress | 已建立 `services/delivery_service/lifecycle.py` 与状态更新入口，当前支持 `queued -> sent -> delivered / failed` 最小流转 |
| provider 成功回执回写 demo | in_progress | 已建立 `provider_delivery_receipt_demo.py` 与校验脚本，可本地演示 `sent -> delivered` 回写并保留 `providerMessageId` |
| provider 失败回执回写 demo | in_progress | 已建立 `provider_delivery_failure_demo.py` 与校验脚本，可本地演示 `sent -> failed` 回写并保留 `providerMessageId` |
| 一键整链演示 | in_progress | 已建立 `full_notification_demo.py` 与校验脚本，可一键演示公告事件 → scheduler → runtime → output → telegram payload → delivery result |
| full notification receipt writeback 入口 | in_progress | 已给 `full_notification_demo.py` 补 `receiptMode` 入口；当前默认 mock 发送路径下会返回 `RECEIPT_NOT_APPLICABLE`，尚不能真正完成整链回执回写 |
| 统一 external entry demo | in_progress | 已建立 `external_entry_demo.py` 与校验脚本，可统一演示 HTTP risk-check、scheduler review、notification review 三类外部入口调用 |
| Binance 主骨架真实接入 | done | `market_data_service` 已真实接通 Binance 主骨架，CLI / runtime / 本地样板均可读取 live 快照 |
| Funding 增强层接入 | in_progress | 已建立 `coinglass_funding.py` 并映射进 `MarketSnapshot`，当前缺可用 Coinglass key / 稳定 endpoint，故按 error/null 优雅降级 |
| Heatmap 增强层接入 | in_progress | 已建立 `coinglass_heatmap.py` 并映射进 `MarketSnapshot`，当前缺可用 Coinglass key / 稳定 endpoint，故按 error/null 优雅降级 |
| GMGN 可行性验证 | blocked | 当前环境下站点、API 与常见路径均返回 403，Cloudflare 拦截仍存在 |
| 风控真实调用链 | in_progress | 已建立 `risk_check_service`，CLI / 统一入口 / runtime / adapter / 本地样板均可调用 live 风控；Funding / Heatmap 当前作为可降级增强字段参与快照 |
| 记录默认正式存储 | in_progress | 默认 repository 已切到 SQLite，旧 JSON 仅作为迁移来源 / 备份；仍缺更系统的迁移与一致性治理 |
| 提醒真实调度链路 | in_progress | 已有公告事件 → scheduler → alert 分流 → output → telegram payload → delivery service → delivery facade → delivery status SQLite 的本地演示链，但尚未建立真实公告监控、真实调度、真实发送与状态回写 |
| 交易计划记录真实查询链路 | in_progress | 已建立 `record_service` + `record_repository`，默认走 SQLite，且已有最小校验；但列表查询、接口治理和完整测试未完成 |
| 复盘真实查询链路 | in_progress | 已建立 `review_service`，已支持按 `userId` 透传查最近记录并输出复盘，但正式查询接口与筛选能力未完成 |

---

## 四、当前项目的真实结论
如果现在要用一句最诚实的话概括当前状态：

> **产品蓝图、Skill 本体、数据结构、实施路线已经完成得比较完整；提醒 / 速评 / 风控 / 记录 / 复盘原型闭环已经跑通；核心 service 层、统一入口层、runtime 入口层、adapter 层、repository 层都已经建立；Binance 主骨架已真实可用；Funding 与 Heatmap 已经进入代码骨架并接入统一快照，但当前仍因缺可用 Coinglass key / 稳定 endpoint 而处于 error/null 可降级状态；GMGN 在当前环境仍被 Cloudflare/403 阻断；与此同时，外部入口层已经从单纯 mock 继续推进到本地 HTTP server、本地 scheduler runner、统一 external entry demo；发送链也已经推进到 OpenClaw message adapter slot、execution slot、formal facade、real/mock 决策策略、统一 result schema、providerMessageId 兼容、queued 入口、最小 lifecycle 骨架、provider 成功/失败回执回写 demo，以及 full notification demo 的 receipt writeback 入口。**

---

## 五、当前最优先事项
如果只保留一个最高优先级，应写为：

# P0：把已建立的 Binance live 主骨架 + Funding/Heatmap 增强层骨架 + HTTP/server + scheduler runner + notification/delivery 过渡层，从本地演示推进到真实外部调用链、真实调度链与真实发送替换链

原因：
- Binance core live 已成立
- Funding / Heatmap 已接进统一快照，当前最缺的是可用 key / 稳定 endpoint，而不是从零开始写骨架
- 当前外部入口层已经不再只是 mock，而是出现了本地 server / runner / unified demo，最自然的下一步就是把它们向真实链路推进
- 发送链现在已经有 queued entry + adapter slot + execution slot + formal facade + clear fallback policy + success/failure writeback demo 的结构，适合继续往真实发送替换层推进
- full notification demo 也已开始暴露 receipt writeback 入口，只是当前 mock 路径下仍不会真正生效
- GMGN 仍 blocked，不应拖住今天的主推进节奏

---

## 六、下一阶段建议
下一阶段建议统一只盯以下顺序推进：

1. 若能拿到可用 Coinglass key，优先把 Funding / Heatmap 从可降级骨架推进到真实可用增强层
2. 继续把本地 HTTP server、本地 scheduler runner、external entry demo 推进到更正式的外部调用链
3. 将提醒链从本地 scheduler 演示推进到真实公告监控 + 真实调度 + 真实发送/状态回写
4. 将 `openclaw_message_delivery_adapter` / `delivery_facade` / `delivery_service` 从过渡层推进到真实发送接口替换层
5. 继续补 delivery status lifecycle、失败处理、回执写回等治理能力
6. 继续补 runtime / adapter / 存储与查询的最小治理能力
7. GMGN 可行性再评估（仅在稳定访问方式出现后）

---

## 七、文档结论
当前项目最不缺的是：
- 方向
- 结构
- 文档
- 契约
- 第一版 service / repository / runtime / adapter 骨架
- Binance core live 主骨架
- Funding / Heatmap 的可降级增强层骨架
- 本地 HTTP server / scheduler runner / unified external entry demo
- 本地提醒输出 / 发送样板
- OpenClaw message adapter slot
- OpenClaw message execution slot
- delivery formal facade / delivery service 过渡层
- delivery facade decision policy
- delivery result schema
- delivery status SQLite 最小回归
- providerMessageId 兼容
- delivery queued entry
- delivery lifecycle skeleton
- provider success/failure writeback demos
- full notification receipt writeback entry

当前项目最缺的是：
- **可用的 Coinglass key / 稳定增强层上游**
- **正式外部调用链接入**
- **正式提醒调度与状态回写**
- **正式发送接口替换与状态治理**
- **更完整的 delivery lifecycle / 失败处理 / 回执接入**
- **更完整的鉴权 / 限流 / 重试 / 审计 / 幂等能力**
- **GMGN 的稳定访问方式**

因此，接下来所有工作都应围绕一句话推进：

> **把已经跑通的 Binance core live、Funding/Heatmap 增强层骨架、HTTP/server、scheduler runner、notification/delivery 过渡层，从“可演示原型 + 已成型分层 + 可降级骨架”推进到“增强层真实可用、正式外部可调用、真实调度可运行、真实发送可替换、状态可追踪、错误更可控、存储更稳定”的 MVP。**
