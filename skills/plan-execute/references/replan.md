# Replan 规程（plan-execute 参考）

本文件给 `plan-execute` skill §5 提供出错与重规划的决策规程。**任务失败或发现计划缺陷时先 `read` 本文件。**

核心原则：**出错不要硬冲**。规划是探索性的，计划必然有错；executor 的工作是识别错误、按规程处置、留下复盘记录。

## 失败分类与处置

任务失败（verification 不过 / acceptance 不可达 / 抛异常）时，按以下顺序判定：

### 1. 可在原 acceptance 内修（最常见）

- 现象：verification 报错明确，acceptance 仍合理，改动范围在 `files` 内。
- 处置：就地修，重跑 verification。
- 重试上限：**2 次**。第三次仍失败 → 升级到 2 或 3。
- 不计入 replan 次数。

### 2. acceptance 本身有缺陷但任务范围不变（局部 replan）

- 现象：acceptance 写得不可测 / 不可达，但任务的目标仍合理，任务边界不变。
- 处置：**局部 replan**——重写该任务的 `acceptance` 与 `verification`，保留任务 id 与 depends。
- 计入 replan 次数（全局上限见下）。
- 在「复盘笔记」记一笔：原 acceptance 缺陷、改成什么、为什么。

### 3. 计划级缺陷（依赖断裂 / 目标不可达）

- 现象：
  - 某任务 `depends` 引用的任务已 `blocked` 或 `abandoned`。
  - 发现需要触碰计划外的关键文件（不属于任何任务的 `files`）。
  - 计划级 `acceptance` 在当前任务集下不可达。
  - 任务尺寸实际是 XL，原分解失败。
- 处置：**标 `plan.status: blocked`**，向用户报告：
  - 哪个任务受阻、试过什么。
  - 缺什么（前置任务、文件、决策、信息）。
  - 建议用户回到 `plan-create` 局部或整体重规划。
- executor 不自行做整体 replan——重规划是 planner 的事；executor 只标 blocked 并交还。

### 4. 收敛上限（防震荡）

全局 replan 计数 ≥ **3 次仍未向 done 收敛** → 标 `plan.status: blocked`，报告"反复 replan 不收敛，疑似目标本身或分解有结构性问题"。避免无限 replan 循环烧 token。

## Replan 时 executor 能改什么、不能改什么

| 改动 | executor 可做？ |
|---|---|
| 单任务的 acceptance / verification（局部 replan） | ✅ |
| 单任务的 `notes` 备注 | ✅ |
| 任务状态（todo/in_progress/done/blocked） | ✅ |
| `plan.status`、`plan.updated` | ✅ |
| 新增/删除任务 | ❌（回 plan-create） |
| 改 `depends` 拓扑 | ❌（回 plan-create） |
| 改 `default_mode` | ❌（用户或 plan-create 决定） |
| 改计划级 `goal` / `acceptance` | ❌（用户的决定） |

**边界清晰**：executor 只在原计划骨架内修补任务级字段；动骨架就交还 planner。

## 触发 replan 的常见信号

| 信号 | 通常意味着 |
|---|---|
| verification 反复同一种错 | acceptance 不可达，或 files 漏标关键文件 |
| 实现需要 import 计划外的模块 | files 不全，或任务边界划错 |
| 任务实际触碰 8+ 文件 | 分解失败，是 XL；交还 plan-create 重拆 |
| 子 agent 报"无法在 acceptance 内完成" | acceptance 与目标不匹配 |
| checkpoint 反复不过 | 该阶段地基有问题；可能要回退前置任务 |
| 跑测试发现既有行为已变 | 计划基于过时现状；交还 plan-create |

## 复盘笔记的写法

每次局部 replan 或 blocked，在计划文件的「复盘笔记」段加一条：

```md
- 2026-07-05 T3 局部 replan（1/3）：原 acceptance "性能更好" 不可测，改为 "p99 < 200ms"。原因：验收写得太虚。
- 2026-07-05 T5 blocked：依赖的 T4 子 agent 报 JwtSession 与既有 CsrfMiddleware 冲突，超出 T4 acceptance。建议 plan-create 加一个 T4.5 处理 CSRF 兼容。
```

复盘笔记是**下次规划复用的资产**——把踩到的坑固化下来，避免同样的计划再错一次。

## 反模式

- **硬冲**：verification 失败就改 verification 让它过——自欺欺人。verification 是真相源，acceptance 才是可改的。
- **越界 replan**：executor 自己加任务、改拓扑——破坏计划的可追溯性。骨架问题交还 planner。
- **静默受阻**：标 blocked 但不写缺什么——用户无法决策。blocked 必须配说明。
- **无限重试**：不设上限，react 重试或 replan 反复到 token 失控——硬上限是 2 次重试 + 3 次 replan。
