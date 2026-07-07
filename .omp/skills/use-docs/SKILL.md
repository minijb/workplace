---
name: use-docs
description: 只读的文档系统导航与结构参考。当需要理解或定位 docs/ 工作区（spec/generated/reference/adr/plan 各目录与各目录 INDEX.md）、术语表（根级 CONTEXT.md、多上下文的 CONTEXT-MAP.md 与模块 CONTEXT.md 的单/多上下文结构），或决定「某样东西该写进哪个目录、该去哪查」时使用。与 docs-workspace 互为正反面——docs-workspace 搭建并写入结构，本 skill 只解释结构、教导航纪律、说明每个文件/目录的作用与边界，并指向 skills/lib/ 下的格式契约；不创建任何文件、不重述格式模板。
---

# 文档系统导航与结构参考

只读地理解与定位本项目的文档系统（`docs/` 工作区 + `CONTEXT.md` 术语表）。**不创建、不修改任何文件——搭建与写入归 `docs-workspace`。**

> **与 docs-workspace 的关系**：`docs-workspace` 是「写入 / 搭建」流程（创建目录、生成 INDEX、初始化 CONTEXT）。本 skill 是「读取 / 导航 / 理解」参考——同样的结构，相反的需求。两者不重复：本 skill 讲「是什么 / 装什么 / 不装什么 / 该去哪」，格式细节一律指向 `skills/lib/`，绝不内联重述。

## 0. 前置：只读

本 skill 全程只读。本 skill 解决「这个系统长什么样、每个部分干什么、我该去哪找 / 放」。若你要**搭建**或**写入**，按意图重定向到对应 skill / lib：

- **搭建**这套结构 → `docs-workspace`（建目录、生成 INDEX、初始化 CONTEXT）。
- **修订 / 新增术语** → `grilling-with-context`（边盘问边把术语落进 `CONTEXT.md`、决策入 `docs/adr/`）；仅搭术语表骨架 → `docs-workspace`。
- **写 / 推进 / 汇总计划** → `plan-execute`（推进）、`plan-track`（只读对账）、`plan-create`（新建）。
- **写 spec / reference / ADR 正文** → 本仓库无专用 skill，由人或对应工作流直接写。
- **仅需查确切格式 / 词表 / 规则** → `skills/lib/*-format.md`（context / index / adr / plan-format.md，**只读参考，不代替写入**）。

> 程序护栏：本 skill 工具调用应只有 `read` / `grep` / `glob` / `ls`；发现即将 `edit` / `write` 立即停下，改走上表重定向。

## 1. 核心导航纪律（始终遵守）

进入 `docs/` 的任何目录前，按此顺序定位信息：

1. **先读 INDEX**：进入任何 `docs/` 子目录，先读该目录 `INDEX.md`（目录页），再按需加载具体文件——禁止盲猜文件名。
2. **术语查 CONTEXT**：遇到项目用语歧义，查根级 `CONTEXT.md`；多上下文仓库先看 `CONTEXT-MAP.md` 定位所属上下文的 `CONTEXT.md`。
3. **具体内容**：按 INDEX 指引加载 `spec/`、`adr/`、`reference/`、`plan/` 中的具体文件。
4. **格式看 lib**：需要某文件的**确切写法**（模板、字段、编号规则）时，去 `skills/lib/` 对应契约（`context-format.md` / `index-format.md` / `adr-format.md` / `plan-format.md`）——lib 为**只读参考，不代替写入**，不在本 skill 内重复。

## 2. 按意图路由（我该去哪）

| 我想…… | 去这里 |
|---|---|
| 看某功能的需求 / 验收标准 / 接口约定 | `docs/spec/`（先读其 `INDEX.md`） |
| 查一个「为什么这么决定」的架构决策 | `docs/adr/`（先读其 `INDEX.md`） |
| 查第三方 API / 标准规范 / 调研引用 | `docs/reference/`（先读其 `INDEX.md`） |
| **查**计划进度 / 状态（权威对账） | `docs/plan/INDEX.md`（看板，可能已 drift）→ `plan-track`（只读遍历树纠偏） |
| **写 / 推进**一份执行计划 | `plan-execute`（推进）；新建计划 → `plan-create` |
| 搞清某个术语到底是什么意思 | 根级 `CONTEXT.md`（多上下文先查 `CONTEXT-MAP.md`） |
| **修订 / 新增**术语 | `grilling-with-context`（边盘问边把术语落进 `CONTEXT.md`）；仅搭骨架 → `docs-workspace` |
| 看工具自动生成的报告 | `docs/generated/`（可能被 gitignore，INDEX 仍维护） |
| 知道某文件的**确切格式 / 词表 / 规则**怎么写 | `skills/lib/*-format.md`（context / index / adr / plan-format.md，**只读参考，不代替写入**） |
| **写** spec / reference / ADR 正文内容 | 本仓库无专用 skill，由人或对应工作流直接写；use-docs 只指路，不代替写入 |
| **搭建**这套结构本身 | `docs-workspace` skill（本 skill 不创建文件） |

> 完整结构总图、每个目录的「装什么 / 不装什么 / 格式契约位置」见 `references/`。

## 3. 结构总览（按需 read）

完整结构解剖下沉到 `references/`，**按触发条件加载**，不要前置全读：

- **`./references/docs-structure.md`** —— 当需要对照 `docs/` 工作区树（spec / generated / reference / adr / plan + 各 INDEX）、或搞清某目录「装什么 / 不装什么 / 格式契约在哪」时加载。
- **`./references/context-structure.md`** —— 当需要搞清术语表放哪、单上下文 vs 多上下文（`CONTEXT-MAP.md`）、术语归属规则时加载。

## 4. 完成标准

- 你已正确定位到所需的 docs 组件（目录 / INDEX / CONTEXT / 具体 spec 或 adr），或定位到所需 lib 契约（`context-format.md` / `index-format.md` / `adr-format.md` / `plan-format.md`）。
- 你清楚它「装什么、不装什么」，并知道去哪个 `skills/lib/` 契约查确切格式。
- 全程未创建或修改任何文件（搭建 → `docs-workspace`；写术语 → `grilling-with-context`；写 / 推进计划 → `plan-execute` / `plan-track`）。

## 不做什么

- 不创建、不修改、不删除任何文件——搭建归 `docs-workspace`。
- 不重述格式模板 / 规则 / 词表——单一真源在 `skills/lib/*-format.md`（context / index / adr / plan-format.md，**只读参考，不代替写入**），本 skill 只指路。
- 不替计划系统写 / 推进 / 汇总计划——写 / 推进归 `plan-execute`（或 `plan-create` 新建），只读对账归 `plan-track`。
- 不修订 / 新增术语——归 `grilling-with-context`（边盘问边落术语）；仅搭术语表骨架归 `docs-workspace`。
- 不写 spec / reference / ADR 正文——本仓库无专用 skill，由人或对应工作流直接写。
- 不把术语表当规格或草稿——CONTEXT.md 只装术语。
