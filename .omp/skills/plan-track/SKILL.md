---
name: plan-track
description: 规划系统的 Tracker 阶段。先读 docs/plan/INDEX.md 再遍历各计划目录的任务树对账，汇总进度、阻塞、下一步动作；可选地按计划或状态过滤。只读——不改计划、不执行任务。需要"这个计划到哪了""哪些计划受阻""下一步该跑什么"时用它。
---

# 计划系统 · 跟踪（Tracker）

只读汇报计划系统的状态。本 skill **绝不写**任何计划文件，只扫、读、汇总。

> **三 skill 关系**：`plan-create`（规划）→ `plan-execute`（执行，写状态）→ `plan-track`（本 skill，读状态汇报）。共享契约 `skills/lib/plan-format.md`——汇报前先 `read` 它确认 Dotted ID、状态词表（plan/leaf/group 派生）、roll-up 规则。
>
> **核心模型**：计划 = 任务树。状态真源——`plan.status` 在 `plan.md`，leaf `status` 在各 leaf 文件，group 状态派生不存储。tracker 据真源汇总并对账。

## 0. 前置：读契约

每次执行本 skill，先 `read skills/lib/plan-format.md`，确认状态词表（plan 级、leaf 级、group 派生）、Dotted ID 解析、roll-up 规则、两层 INDEX 结构。**禁止凭记忆汇报字段。**

## 1. 发现计划

- 先 `read docs/plan/INDEX.md`——扁平计划注册表，分「进行中（active/）」「已完成（completed/）」两段，路径指向**计划目录**。
- 再 `glob docs/plan/active/*/plan.md` 与 `docs/plan/completed/*/plan.md` **对账**：INDEX 缺记或多记的目录都要标出（drift）。状态以各 `plan.md` frontmatter 为准，不轻信 INDEX 的进度数字。
- INDEX 是发现入口与轻量看板，但**不是状态真源**——`plan.md` 与 leaf 文件才是。

若用户指定某个计划（按 id 或目录名），直接定位该目录，跳到 §2。

## 2. 汇总单计划

对指定计划，`read` 其 `plan.md`，然后**遍历任务树**（从根 `INDEX.md` 起递归读各 group `INDEX.md` 与 leaf 文件），汇报：

- **元信息**：title、status、default_mode、created、updated。
- **进度**：leaf 总数 / done / in_progress / todo / blocked（按 leaf `status` 统计）。group 不计入执行统计，但显示其派生状态。
- **下一步**：列出所有就绪 leaf（`todo` 且 `depends` 全 done——Dotted ID 解析后前置为 done leaf 或 done group）。这些是 executor 接下来该做的。若 subagent/hybrid 模式，指出它们是否构成可并行波次（无 files 冲突）。
- **阻塞链**：所有 `blocked` leaf 及其前置链；从 `plan.md`「复盘笔记」取受阻原因。
- **检查点**：最近的 checkpoint 是否已过；下一个 checkpoint 边界距当前进度几个 leaf。
- **计划级验收**：`plan.acceptance` 当前是否已可校验（所有相关 leaf done）。
- **roll-up 对账**：抽查若干 group `INDEX.md` 的派生状态行，与按子节点重算的结果比对——不一致即标 drift（说明 execute 漏刷新）。

## 3. 汇总多计划（默认视图）

未指定单个计划时，给所有计划的概览：

| id | title | status | 进度 (done leaf / total leaf) | default_mode | updated | 就绪 leaf 数 |
|---|---|---|---|---|---|---|

按 `updated` 倒序。突出：

- 任何 `blocked` 计划——置顶并附受阻摘要。
- 任何 `in_progress` 计划——次置顶。
- `ready` 但未启动的计划——列出，提示可执行。

## 4. 过滤

按需过滤：

- `--status blocked`：只列受阻计划/leaf。
- `--status in_progress`：正在跑的。
- `--ready-leaves`：跨计划列出所有就绪 leaf（executor 视角的下一步）。
- `--mode <react|subagent|hybrid>`：按默认模式过滤。

无过滤参数时给 §3 的默认概览。

## 5. 输出格式

汇报**简洁、可扫**：

- 多计划：一张表 + 受阻/进行中标红提示。
- 单计划：元信息 + 进度条（done leaf / total leaf）+ 下一步动作清单 + 阻塞（若有）+ 树形概览（group/leaf 含派生状态）。
- **不照抄计划正文**——用户要看进度，不是重读计划。背景与依赖图等让用户自行打开文件看。

## 完成标准

- 汇总基于实际 `read` 到的文件内容（`plan.md` + leaf 文件 + group INDEX），不靠记忆或猜测。
- 进度数字与 leaf `status` 严格对应（统计可重复）；group 派生状态与 roll-up 规则一致。
- 「下一步」列出的 leaf 确实是就绪的（`depends` 全 done，Dotted ID 解析正确）。
- 受阻项有原因（从复盘笔记或 blocked leaf 上下文提取），不只是"它受阻了"。
- 全程零写入：计划目录、`plan.md`、leaf 文件、任何 INDEX 都未被本 skill 改动。

## 不做什么

- 不执行任务、不改状态——那是 `plan-execute`。
- 不创建/修改计划或任务树——那是 `plan-create`。
- 不写 `docs/plan/INDEX.md` 或任何 group `INDEX.md`——本 skill 绝不写任何计划文件；INDEX 由 create/execute 维护，track 只读并对账。
- 不替用户决策"接下来该跑哪个计划"——只列事实，决策留给用户。
