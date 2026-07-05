---
name: plan-track
description: 规划系统的 Tracker 阶段。扫描 docs/plan/*.md 读 frontmatter 与任务状态，汇总进度、阻塞、下一步动作；可选地按计划或状态过滤。只读——不改计划、不执行任务。需要"这个计划到哪了""哪些计划受阻""下一步该跑什么"时用它。
---

# 计划系统 · 跟踪（Tracker）

只读汇报计划系统的状态。本 skill **绝不写**计划文件，只扫、读、汇总。

> **三 skill 关系**：`plan-create`（规划）→ `plan-execute`（执行，写状态）→ `plan-track`（本 skill，读状态汇报）。共享契约 `skills/lib/plan-format.md`——汇报前先 `read` 它确认状态/模式词表。

## 0. 前置：读契约

每次执行本 skill，先 `read skills/lib/plan-format.md`，确认状态词表（plan 级、task 级）与 frontmatter 字段名。**禁止凭记忆汇报字段。**

## 1. 发现计划

- `glob docs/plan/*.md` 列出全部计划文件。
- 对每个文件，`read` 取 frontmatter（`id` / `title` / `status` / `default_mode` / `updated` / `goal`）。
- 这是计划系统的**发现机制**——`docs/plan/` 没有 INDEX.md，靠扫文件读 frontmatter。

若用户指定某个计划（按 id 或文件名），直接定位该文件，跳到 §2。

## 2. 汇总单计划

对指定计划，`read` 整个文件，汇报：

- **元信息**：title、status、default_mode、created、updated。
- **进度**：任务总数 / done / in_progress / todo / blocked，按 status 统计。
- **下一步**：列出所有就绪任务（`todo` 且 `depends` 全 `done`）——这些是 executor 接下来该做的。若用 subagent/hybrid 模式，指出它们是否构成可并行波次（无 files 冲突）。
- **阻塞链**：所有 `blocked` 任务及其前置链；从「复盘笔记」取受阻原因。
- **检查点**：最近的 checkpoint 是否已过；下一个 checkpoint 边界距当前进度几个任务。
- **计划级验收**：`plan.acceptance` 当前是否已可校验（所有相关任务 done）。

## 3. 汇总多计划（默认视图）

未指定单个计划时，给所有计划的概览：

| id | title | status | 进度 (done/total) | default_mode | updated | 就绪任务数 |
|---|---|---|---|---|---|---|

按 `updated` 倒序。突出：

- 任何 `blocked` 计划——置顶并附受阻摘要。
- 任何 `in_progress` 计划——次置顶。
- `ready` 但未启动的计划——列出，提示可执行。

## 4. 过滤

按需过滤：

- `--status blocked`：只列受阻计划/任务。
- `--status in_progress`：正在跑的。
- `--ready-tasks`：跨计划列出所有就绪任务（executor 视角的下一步）。
- `--mode <react|subagent|hybrid>`：按默认模式过滤。

无过滤参数时给 §3 的默认概览。

## 5. 输出格式

汇报**简洁、可扫**：

- 多计划：一张表 + 受阻/进行中标红提示。
- 单计划：元信息 + 进度条（done/total）+ 下一步动作清单 + 阻塞（若有）。
- **不照抄计划正文**——用户要看进度，不是重读计划。背景与依赖图等让用户自行打开文件看。

## 完成标准

- 汇总基于实际 `read` 到的文件内容，不靠记忆或猜测。
- 进度数字与任务 status 行严格对应（统计可重复）。
- 「下一步」列出的任务确实是就绪的（`depends` 全 done）。
- 受阻项有原因（从复盘笔记或 blocked 任务上下文提取），不只是"它受阻了"。
- 全程零写入：计划文件、frontmatter、任务状态都未被本 skill 改动。

## 不做什么

- 不执行任务、不改状态——那是 `plan-execute`。
- 不创建/修改计划——那是 `plan-create`。
- 不在 `docs/plan/` 建 INDEX——发现靠扫 `*.md` 读 frontmatter（本 skill §1）。
- 不替用户决策"接下来该跑哪个计划"——只列事实，决策留给用户。
