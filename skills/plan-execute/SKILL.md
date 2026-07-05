---
name: plan-execute
description: 规划系统的 Executor 阶段。读取一份 docs/plan/ 下的 ready/in_progress 计划，按其 default_mode（react / subagent / hybrid）推进任务、跑 verification、更新任务与计划状态。用户可以显式指定执行模式覆盖计划的默认值。出错时按 replan 规程处理。不创建计划——创建归 plan-create，查进度归 plan-track。
---

# 计划系统 · 执行（Executor）

按一份既定计划把任务跑完。本 skill 是计划系统的**写入**阶段：推进任务状态、跑验证、必要时 replan。**只执行计划里的任务，不自创新任务。**

> **三 skill 关系**：`plan-create`（规划）→ `plan-execute`（本 skill，执行）→ `plan-track`（查进度）。共享契约 `skills/lib/plan-format.md`——**执行前先 `read` 它**，确认状态/模式词表与字段名。

## 0. 前置：读契约、读计划

1. `read skills/lib/plan-format.md`——确认字段、状态、模式词表（每次执行都读，不靠记忆）。
2. `read` 用户指定的计划文件（或扫 `docs/plan/*.md` 取 `status: ready`/`in_progress` 中最新的）。
3. **读全文件**再动笔——避免覆盖并发改动。

## 1. 确认执行模式

计划 frontmatter 的 `default_mode` 是默认。用户可在调用时显式覆盖：

- 用户指定 `react` / `subagent` / `hybrid` → 本次全程用指定模式（不改写计划的 `default_mode`，仅本次覆盖）。
- 用户未指定 → 用计划 `default_mode`。

单任务 frontmatter 的 `mode` 字段**始终生效**（它覆盖本次会话的默认）。若用户显式指定 `react`，仍尊重任务级 `mode`（如某任务硬要求 subagent 并行）。

**三种模式的执行协议见 `references/modes.md`——切模式前先 `read` 对应章节。** 速览：

| 模式 | 协议 |
|---|---|
| `react` | 单线程串行：取下个就绪任务→实现→跑 verification→更新状态→下一个 |
| `subagent` | DAG 调度：按依赖分波，无依赖任务派发子 agent 并行，波次间 barrier |
| `hybrid` | react 骨架 + 波次并行：串行推进依赖链，遇独立波次切 subagent |

## 2. 取下个就绪任务

一个任务"就绪"当且仅当：

- `status: todo`
- `depends` 中所有 id 的任务 `status: done`

若多个任务就绪：

- `react`：取拓扑序最前的。
- `subagent` / `hybrid`：**全部**就绪任务组成一个波次并行派发（详见 `references/modes.md`）。

若无就绪任务且有 `in_progress` → 继续该任务。若无就绪且无 `in_progress`、还有 `todo` → 说明前置链断了，进 §5 replan 或标 `blocked`。

## 3. 执行单任务（react / 单任务视角）

不论整体模式，**单个任务**的执行循环节奏：

1. **改状态**：`read` 计划文件，把该任务 `status` 从 `todo` 改 `in_progress`；刷新 `plan.updated`；`write` 回去（写全文件，不要局部补丁）。
2. **实现**：按 `acceptance` 做最小改动满足之。触碰 `files` 列出的路径；发现需要触碰计划外的文件，先在 `notes` 备注。
3. **验证**：跑 `verification` 命令。失败 → 修；反复失败超 2 次 → 进 §5。
4. **验收**：逐条核对 `acceptance`——全部可观察满足才算完成。
5. **改状态**：`status: done`；刷新 `plan.updated`；`write`。
6. **检查点**：若该任务属于某 checkpoint 的边界，暂停跑检查点验证；失败则不继续，进 §5 或请求人审。

**写状态用 `write` 写全文件**，不用 `edit` 局部改——计划文件是唯一真源，写全文件避免遗漏并发改动。

## 4. 检查点

到达 checkpoint 边界时：

- 跑该 checkpoint 列出的全部验证。
- 全过 → 继续。
- 任一失败 → 不跨过 checkpoint。优先就地修；修不动进 §5；属于不可逆或人审门 → 暂停并向用户报告，等指示。

## 5. 出错与 Replan

任务失败、验证反复不过、发现计划缺陷（acceptance 不可达、依赖缺失、files 漏标关键文件）时，**不要硬冲**。**Replan 规程见 `references/replan.md`——出错时先 `read` 它。** 决策树速览：

```
任务失败
├─ 可在原 acceptance 内修 → 修，重试 ≤2 次
├─ acceptance 本身有缺陷/不可达 → 局部 replan：改任务（不超过本计划范围）
├─ 计划级缺陷（依赖断裂、目标不可达）→ 标 plan.status: blocked，向用户报告
└─ 触发收敛上限（全局 replan ≥3 次仍未收敛）→ 标 blocked
```

replan 后必须刷新 `plan.updated` 并在「复盘笔记」段记一笔（改了什么、为什么）。

## 6. 计划级完成

全部任务 `done` **不等于**计划完成。executor 必须再：

1. 逐条核对计划级 `acceptance`——全部可观察满足。
2. 跑所有 checkpoint 验证。
3. 全过 → `plan.status: done`；刷新 `updated`。
4. 在「复盘笔记」段简记：实际模式与计划的偏差、踩到的坑、对后续计划的建议。

任一不满足 → 不置 `done`；能修则修，不能修标 `blocked` 并报告缺什么。

## 7. 完成标准（本 skill 的退出条件）

- 要么 `plan.status: done`（计划级 acceptance 全满足）；
- 要么 `plan.status: blocked`（受阻且无法自解，已写明缺什么、试过什么）；
- 要么用户中断。
- 退出前所有改动已 `write` 落盘；`plan.updated` 已刷新；复盘笔记已记。

## 不做什么

- 不创建计划、不改任务分解——那是 `plan-create`。replan 仅在出错时局部修，不重做规划。
- 不查询进度报表——那是 `plan-track`。executor 改状态，不生成汇报。
- 不越界：只做任务 `acceptance` 内的事；发现额外需求写进 `notes`，不擅自扩。
- 不在 `docs/plan/` 建 INDEX——发现机制是扫 `*.md`（见 plan-track）。
