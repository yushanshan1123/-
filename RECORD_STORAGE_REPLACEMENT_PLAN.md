# RECORD_STORAGE_REPLACEMENT_PLAN.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档用于定义：

> **如何把当前基于 JSON 文件的交易记录原型，替换成正式存储层。**

当前项目已经跑通了：
- 风控 → 记录
- 记录 → 复盘

但这两条链现在仍然依赖：
- `trade_review_records.json`

这在原型阶段是可以接受的，
但要进入可持续运行的 MVP，就必须尽快替换成更正式的存储方式。

---

## 一、为什么现在必须处理存储层
当前 JSON 文件方案的问题很直接：

### 1. 不适合多用户
所有记录都堆在一个文件里，后续一旦有多个用户，管理会很混乱。

### 2. 不适合并发写入
只要写入频率上来，就会有覆盖、冲突、损坏风险。

### 3. 不适合查询扩展
现在只能简单读取最近一条。  
后面如果要支持：
- 按用户查
- 按交易对查
- 按结果筛选
- 按时间排序

JSON 文件会越来越难用。

### 4. 不适合正式服务链路
原型阶段可以接受“文件存一下”，
但正式 service 如果还靠 JSON 文件，会一直卡在演示级能力。

---

## 二、当前存储层现状
当前与记录相关的逻辑主要分布在：

- `services/record_service/service.py`
- `services/review_service/service.py`
- `trade_review_records.json`

### 当前已具备的能力
- 创建记录
- 读取最近记录
- 更新结果
- 生成复盘

### 当前缺失的能力
- 正式持久化
- 多用户隔离
- 稳定查询接口
- 更清晰的存储边界

---

## 三、正式替换目标
下一阶段不一定立刻上复杂数据库，
但至少要做到：

> **记录读写，不再直接依赖 JSON 文件。**

建议目标拆成两层：

### Phase 1 目标
先把“文件读写逻辑”抽象成正式 repository 接口。

### Phase 2 目标
再把 repository 的底层实现，从 JSON 文件切到正式数据库或更可靠存储。

---

## 四、推荐目标结构
建议新增一层：

## `record_repository`

这样服务层分工会更清楚：

### `record_service`
负责业务动作：
- 创建记录
- 查询记录
- 调用 repository

### `review_service`
负责复盘逻辑：
- 读取记录
- 更新结果
- 生成复盘内容

### `record_repository`
负责存储动作：
- save
- get latest
- get by id
- list by user
- update

---

## 五、第一步最合理的替换方式
现在最稳的做法不是马上接复杂数据库，
而是：

# 先抽 repository 边界

也就是先把这些逻辑从 service 里抽出去：

- `load_records()`
- `save_records()`
- `get_latest_record()`
- `update_record_result()`

先让 service 不再关心“底层到底是文件还是数据库”。

这一步做完后，
后面想换 SQLite、Postgres、其他存储，都不会伤到业务层太多。

---

## 六、推荐的第一版 repository 能力
建议第一版至少有这些函数：

### 1. `create_record(record)`
用于保存新记录

### 2. `get_latest_record(user_id=None)`
用于取最近一条记录

### 3. `get_record_by_id(trade_id)`
用于按 ID 查一条记录

### 4. `list_records(user_id=None, filters=None)`
用于后续扩展列表查询

### 5. `update_record(trade_id, patch)`
用于更新结果、备注、时间等字段

---

## 七、正式存储方案建议
### 最推荐的过渡方案
如果要在 MVP 阶段尽量稳、尽量轻，
我建议优先考虑：

# SQLite

### 为什么
- 比 JSON 文件稳很多
- 比上完整数据库轻很多
- 单机原型 / MVP 很合适
- 查询能力足够支撑记录 / 复盘
- 后面再迁数据库也比从 JSON 迁容易

---

## 八、不建议现在直接做什么
为了避免工程过重，当前阶段不建议：

- 一上来就上复杂 ORM
- 一上来就上远程数据库
- 一上来就设计特别复杂的表关系

因为当前最重要的是：

> **先把 JSON 文件从业务层里拿出去。**

---

## 九、建议替换顺序
建议按这个顺序推进：

### Step 1
新增 `record_repository` 抽象层

### Step 2
把 JSON 文件读写迁到 repository 内部

### Step 3
让 `record_service` 和 `review_service` 只调 repository

### Step 4
跑回归测试，确认：
- 风控 → 记录 正常
- 记录 → 复盘 正常

### Step 5
再考虑把 repository 底层从 JSON 切换到 SQLite

---

## 十、替换完成的判断标准
这一轮什么时候算完成？

不是“数据库已经上线”，
而是以下 4 条成立：

- [ ] service 层不再直接读写 JSON 文件
- [ ] 已存在独立 `record_repository`
- [ ] 风控 → 记录 仍然正常
- [ ] 记录 → 复盘 仍然正常

只要这 4 条成立，就说明存储替换已经走出第一步了。

---

## 十一、当前阶段一句话结论
当前最正确的存储推进方式不是一口气上重型数据库，
而是：

> **先把 JSON 文件读写从 service 里抽到 repository 层，再逐步把 repository 底层切成更正式的存储实现。**

这会是新币合约交易冷静器 2.1 从“原型闭环可演示”走向“正式 MVP 可持续运行”的关键一步。
