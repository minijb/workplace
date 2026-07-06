# Replan 规程（plan-execute 参考）

本文件给 `plan-execute` skill §5 提供出错与重规划的决策规程。**leaf 失败或发现计划缺陷时先 `read` 本文件。**

核心原则：**出错不要硬冲**。规划是探索性的，计划必然有错；executor 的工作是识别错误、按规程处置、留下复盘记录。

> 边界：executor 只在**单个 leaf** 内修补；动**任务树结构**（加/删/改 group 或 leaf 节点、改 Dotted ID 拓扑）就交还 `plan-create`。

## 失败分类与处置

leaf 失败（verification 不过 / acceptance 不可达 / 抛异常）时，按以下顺序判定：

### 1. 可在原 acceptance 内修（最常见）

- 现象：verification 报错明确，acceptance 仍合理，改动范围在 `files` 内。
- 处置：就地修，重跑 verification。
- 重试上限：**2 次**。第三次仍失败 → 升级到 2 或 3。
- 不计入 replan 次数。

### 2. acceptance 本身有缺陷但 leaf 范围不变（局部 replan）

- 现象：acceptance 写得不可测 / 不可达，但该 leaf 的目标仍合理，leaf 边界不变。
- 处置：**局部 replan**——重写该 leaf 的 `acceptance` 与 `verification`，保留 leaf 的 `id` 与 `depends`。
- 计入 replan 次数（全局上限见下）。
- 在 `plan.md`「复盘笔记」记一笔：原 acceptance 缺陷、改成什么、为什么。

### 3. 计划级缺陷（依赖断裂 / 目标不可达 / 需动树结构）

- 现象：
  - 某 leaf `depends` 引用的节点已 `blocked` 或整棵计划被放弃。
  - 发现需要触碰计划外的关键文件（不属于任何 leaf 的 `files`）。
  - 计划级 `acceptance` 在当前 leaf 集下不可达。
  - 某 leaf 实际是 XL，需拆成 group + 子 leaf（动树结构，超出 executor 职权）。
- 处置：**标 `plan.status: blocked`**，向用户报告：
  - 哪个 leaf 受阻、试过什么。
  - 缺什么（前置 leaf、文件、决策、信息）。
  - 建议用户回到 `plan-create` 局部或整体重规划（拆 leaf、改树）。
- executor 不自行做整体 replan——重规划（动树）是 planner 的事；executor 只标 blocked 并交还。

### 4. 收敛上限（防震荡）

全局 replan 计数 ≥ **3 次仍未向 done 收敛** → 标 `plan.status: blocked`，报告"反复 replan 不收敛，疑似目标本身或分解有结构性问题"。避免无限 replan 循环烧 token。

## Replan 时 executor 能改什么、不能改什么

| 改动 | executor 可做？ |
|---|---|
| 单个 leaf 的 `acceptance` / `verification`（局部 replan） | ✅ |
| 单个 leaf 的 `notes` 备注 | ✅ |
| leaf 状态（todo/in_progress/done/blocked） | ✅ |
| `plan.status`、`plan.updated` | ✅ |
| 刷新 group `INDEX.md` 的派生状态行（roll-up） | ✅ |
| 新增/删除 group 或 leaf 节点 | ❌（回 plan-create） |
| 改 Dotted ID / `depends` 拓扑 / group 结构 | ❌（回 plan-create） |
| 改 `default_mode` | ❌（用户或 plan-create 决定） |
| 改计划级 `goal` / `acceptance` | ❌（用户的决定） |

**边界清晰**：executor 只在原树骨架内修补 leaf 级字段；动骨架就交还 planner。

## 触发 replan 的常见信号

| 信号 | 通常意味着 |
|---|---|
| verification 反复同一种错 | leaf acceptance 不可达，或 files 漏标关键文件 |
| 实现需要 import 计划外的模块 | files 不全，或 leaf 边界划错 |
| leaf 实际触碰 8+ 文件 | 分解失败，该 leaf 是 XL；交还 plan-create 拆成 group |
| 子 agent 报"无法在 acceptance 内完成" | acceptance 与目标不匹配 |
| checkpoint 反复不过 | 该阶段地基有问题；可能要回退前置 leaf |
| 跑测试发现既有行为已变 | 计划基于过时现状；交还 plan-create |

## 复盘笔记的写法

每次局部 replan 或 blocked，在 `plan.md`「复盘笔记」段加一条：

```md
- 2026-07-05 leaf 1.3 局部 replan（1/3）：原 acceptance "性能更好" 不可测，改为 "p99 < 200ms"。原因：验收写得太虚。
- 2026-07-05 leaf 2.1 blocked：依赖的 leaf 1.2 子 agent 报 JwtSession 与既有 CsrfMiddleware 冲突，超出 1.2 acceptance。建议 plan-create 在 group 1 下加一个 leaf 1.3 处理 CSRF 兼容。
```

复盘笔记是**下次规划复用的资产**——把踩到的坑固化下来，避免同样的计划再错一次。

## 反模式

- **硬冲**：verification 失败就改 verification 让它过——自欺欺人。verification 是真相源，acceptance 才是可改的。
- **越界 replan**：executor 自己加/删 leaf、改树——破坏计划的可追溯性。树结构问题交还 planner。
- **静默受阻**：标 blocked 但不写缺什么——用户无法决策。blocked 必须配说明。
- **无限重试**：不设上限，react 重试或 replan 反复到 token 失控——硬上限是 2 次重试 + 3 次 replan。
