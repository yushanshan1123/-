# REAL_INTEGRATION_ROADMAP.md

## 项目名称
新币合约交易冷静器 2.1

## 文档目标
这份文档不是继续讨论概念，而是把 **真实数据接入的执行顺序** 固定下来。

---

## 一、当前最新进度判断
接入顺序仍然保持不变：

**Binance 主骨架 → Funding → 清算热力 → GMGN**

但当前真实仓库状态已经更新为：

### 已完成到可用层
- **Binance 主骨架：已真实接通并进入核心 live-ready**

### 已完成到骨架层
- **Funding：已接入统一快照骨架，但当前缺可用 Coinglass key / 稳定 endpoint，故按 error/null 降级**
- **Heatmap：已接入统一快照骨架，但当前缺可用 Coinglass key / 稳定 endpoint，故按 error/null 降级**

### 仍阻塞
- **GMGN：当前环境下仍 403 / Cloudflare blocked**

---

## 二、当前执行优先级的最新含义
### Phase 1：Binance 主骨架
当前状态：**done / core live-ready**

### Phase 2：Coinglass Funding Rate
当前状态：**in_progress / connector skeleton integrated**

### Phase 3：Coinglass 清算热力
当前状态：**in_progress / connector skeleton integrated**

### Phase 4：GMGN.ai 聪明钱层
当前状态：**blocked**

---

## 三、当前最重要的执行结论
如果现在只问一句：

> **下一步最该干嘛？**

答案已经不是继续打磨 Binance，
而是：

# 优先让 Funding / Heatmap 从“可降级骨架”推进到“真实可用增强层”

前提是：
- 拿到可用的 Coinglass key
- 或确认稳定可用的 endpoint 口径

如果这一步当前拿不到，就继续推进：
- 外部调用链接入
- 调度链
- 发送链

而不是继续在 GMGN 上死耗。

---

## 四、文档结论
当前真实接入顺序仍固定为：

**Binance 主骨架 → Funding → 清算热力 → GMGN**

但当前实际进度已经是：

> **Binance 已真实 ready；Funding / Heatmap 已接入骨架但当前降级；GMGN 仍 blocked。**
