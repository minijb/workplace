---
name: use-docs
description: 只读的文档系统导航与结构参考。当需要理解或定位 docs/ 工作区（spec/generated/reference/adr/plan 各目录与各目录 INDEX.md）、术语表（根级 CONTEXT.md、多上下文的 CONTEXT-MAP.md 与模块 CONTEXT.md 的单/多上下文结构），或决定「某样东西该写进哪个目录、该去哪查」时使用。与 docs-workspace 互为正反面——docs-workspace 搭建并写入结构，本 skill 只解释结构、教导航纪律、说明每个文件/目录的作用与边界，并指向 skills/lib/ 下的格式契约；不创建任何文件、不重述格式模板。
---

# 文档系统导航与结构参考

只读地理解与定位本项目的文档系统（`docs/` 工作区 + `CONTEXT.md` 术语表）。**不创建、不修改任何文件——搭建与写入归 `docs-workspace`。**

> **与 docs-workspace 的关系**：`docs-workspace` 是「写入 / 搭建」流程（创建目录、生成 INDEX、初始化 CONTEXT）。本 skill 是「读取 / 导航 / 理解」参考——同样的结构，相反的需求。两者不重复：本 skill 讲「是什么 / 装什么 / 不装什么 / 该去哪」，格式细节一律指向 `skills/lib/`，绝不内联重述。

## 0. 前置：只读

本 skill 全程只读。若你要**搭建**或**写入** docs，用 `docs-workspace`（建结构）或对应格式契约（写内容）。本 skill 解决「这个系统长什么样、每个部分干什么、我该去哪找 / 放」。

## 1. 核心导航纪律（始终遵守）

进入 `docs/` 的任何目录前，按此顺序定位信息：

1. **先读 INDEX**：进入任何 `docs/` 子目录，先读该目录 `INDEX.md`（目录页），再按需加载具体文件——禁止盲猜文件名。
2. **术语查 CONTEXT**：遇到项目用语歧义，查根级 `CONTEXT.md`；多上下文仓库先看 `CONTEXT-MAP.md` 定位所属上下文的 `CONTEXT.md`。
3. **具体内容**：按 INDEX 指引加载 `spec/`、`adr/`、`reference/`、`plan/` 中的具体文件。
4. **格式看 lib**：需要某文件的**确切写法**（模板、字段、编号规则）时，去 `skills/lib/` 对应契约——不在本 skill 内重复。

## 2. 按意图路由（我该去哪）

| 我想…… | 去这里 |
|---|---|
| 看某功能的需求 / 验收标准 / 接口约定 | `docs/spec/`（先读其 `INDEX.md`） |
| 查一个「为什么这么决定」的架构决策 | `docs/adr/`（先读其 `INDEX.md`） |
| 查第三方 API / 标准规范 / 调研引用 | `docs/reference/`（先读其 `INDEX.md`） |
| 看 / 写一份执行计划 | `docs/plan/`（先读 `docs/plan/INDEX.md`；由 plan-create / execute / track 托管） |
| 搞清某个术语到底是什么意思 | 根级 `CONTEXT.md`（多上下文先查 `CONTEXT-MAP.md`） |
| 看工具自动生成的报告 | `docs/generated/`（可能被 gitignore，INDEX 仍维护） |
| 知道某文件的**确切格式**怎么写 | `skills/lib/*-format.md`（不在本 skill 重述） |
| **搭建**这套结构本身 | `docs-workspace` skill（本 skill 不创建文件） |

> 完整结构总图、每个目录的「装什么 / 不装什么 / 格式契约位置」见 `references/`。

## 3. 结构总览（按需 read）

完整结构解剖下沉到 `references/`，需要详细对照时按需加载：

- **`./references/docs-structure.md`** —— `docs/` 工作区完整树（spec / generated / reference / adr / plan + 各 INDEX）+ 每个目录 / 文件的作用、写入边界（什么不进这里、该去哪）、格式契约路径。还包含 `skills/lib/` 格式契约清单与它们和 docs 的关系。
- **`./references/context-structure.md`** —— 术语表系统：根级 `CONTEXT.md` 的段落结构、单上下文 vs 多上下文（`CONTEXT-MAP.md`）、术语归属规则、什么不该进 CONTEXT.md、格式契约路径。

## 4. 完成标准

- 你已正确定位到所需的 docs 组件（目录 / INDEX / CONTEXT / 具体 spec 或 adr）。
- 你清楚它「装什么、不装什么」，并知道去哪个 `skills/lib/` 契约查确切格式。
- 全程未创建或修改任何文件（写入 / 搭建归 docs-workspace 或对应 skill）。

## 不做什么

- 不创建、不修改、不删除任何文件——搭建归 `docs-workspace`。
- 不重述格式模板 / 规则 / 词表——单一真源在 `skills/lib/*-format.md`，本 skill 只指路。
- 不替计划系统写 / 推进 / 汇总计划——归 `plan-create` / `plan-execute` / `plan-track`。
- 不把术语表当规格或草稿——CONTEXT.md 只装术语。
