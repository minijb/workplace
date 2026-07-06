---
name: docs-workspace
description: 检查项目根目录结构并搭建标准化的文档工作区（docs/spec、generated、reference、adr、plan），为 docs 下每个目录建立 INDEX.md 索引，并初始化递归 CONTEXT.md 术语表，用于在人与 LLM 之间对齐项目级知识与通用术语。适用于初始化新项目或规整既有项目的知识目录。
---

# 文档工作区初始化

本技能检查项目根目录结构，并按统一约定搭建文档工作区。**仅创建缺失项，绝不覆盖或删除已有文件。**

> **核心习惯（始终遵守）**：每次需要查阅 `docs/` 下任何文件前，**先读该目录的 `INDEX.md`**，再根据索引按需加载具体文件；新增或删除文件时同步更新同级 `INDEX.md`。

## 1. 检查根目录结构

在创建任何内容前，先用 `glob` / `read` 扫描项目根目录，明确现状：

- 是否已存在 `docs/` 及其子目录（`spec`、`generated`、`reference`、`adr`、`plan`）与各目录的 `INDEX.md`。
- 是否已存在根级 `CONTEXT.md` 或 `CONTEXT-MAP.md`。
- 主要源码目录（如 `src/`、`app/`、`packages/`）——用于判断是否存在多个限界上下文。
- 是否纳入版本控制（`.git/`），以及 `docs/generated/` 是否需要被 `.gitignore` 忽略。

**只有「缺失」的项才需要创建。** 已存在的全部跳过。

## 2. 工作区目录结构

单上下文仓库（多数情况）：

```
/
├── CONTEXT.md                 # 根级术语表（人机共享的通用语）
├── docs/
│   ├── INDEX.md               # 登记各子目录
│   ├── spec/INDEX.md          # 功能规格
│   ├── generated/INDEX.md     # 生成报告（建议入 .gitignore）
│   ├── reference/INDEX.md     # 外部知识
│   ├── adr/INDEX.md           # 架构决策记录
│   └── plan/                  # 计划系统托管（见 §3）
│       ├── INDEX.md           # 计划索引（结构异于其他 INDEX，见 §4）
│       ├── active/            # 非终态：进行中/受阻/放弃
│       └── completed/         # 仅 status: done
└── src/
```

多上下文仓库（多模块 / monorepo），根级同时放 `CONTEXT.md`（项目级共用术语）与 `CONTEXT-MAP.md`，各上下文目录内各放一份 `CONTEXT.md`：

```
/
├── CONTEXT.md               # 项目级共用术语（跨上下文通用）
├── CONTEXT-MAP.md
├── docs/
│   ├── INDEX.md
│   ├── spec/INDEX.md
│   ├── generated/INDEX.md
│   ├── reference/INDEX.md
│   ├── adr/INDEX.md
│   └── plan/                  # 计划系统托管（见 §3）
│       ├── INDEX.md           # 计划索引（结构异于其他 INDEX，见 §4）
│       ├── active/            # 非终态：进行中/受阻/放弃
│       └── completed/         # 仅 status: done
└── src/
    ├── ordering/CONTEXT.md
    └── billing/CONTEXT.md
```

是否多上下文，依据第 1 步对源码目录的扫描结果判断（有多个相互独立、各自具备完整领域语义的模块即为多上下文；仅分层不算）；不确定时询问用户。

## 3. 各目录职责

| 目录 | 职责 | 写入时机 |
|---|---|---|
| `docs/` | 项目级知识数据的总入口，承载跨团队共享的长期记忆 | 立即创建 |
| `docs/spec/` | 功能规格：PRD、需求清单、接口约定、验收标准 | 第一次定义功能时 |
| `docs/generated/` | 自动生成的产物：分析报告、迁移计划、审计输出 | 由工具生成时；建议加入 `.gitignore` |
| `docs/reference/` | 外部知识：第三方 API 摘要、标准/规范引用、调研笔记 | 引入外部依赖或约束时 |
| `docs/adr/` | 架构决策记录：`NNNN-slug.md` | 决策「难以回退」时（判定见 `skills/lib/adr-format.md`） |
| `docs/plan/` | 计划目录（任务树）：**由「计划系统」（planning system）托管**——`plan-create` 写入、`plan-execute` 推进、`plan-track` 汇总，三者共享格式 `skills/lib/plan-format.md`。一个计划是一个**目录树**（group 目录 + leaf 文件）。本技能只创建 `active/`、`completed/` 子目录与顶层 `INDEX.md` 骨架（两段空表），不维护计划内容 | 立即创建（含子目录与 INDEX 骨架） |
| `*/INDEX.md` | 本目录文件的路径与一句话描述 | 目录下文件增删时同步 |

> **计划系统已实现**：`docs/plan/` 由三个 skill 托管——`plan-create`（规划，在 `active/<slug>-<date>/` 写入任务树）、`plan-execute`（执行 leaf、刷新 roll-up；`done` 时把**整个计划目录**移入 `completed/`）、`plan-track`（只读汇总，先读顶层 INDEX 再遍历树对账）。格式契约见 `skills/lib/plan-format.md`。本技能创建 `active/`、`completed/` 与顶层 `INDEX.md` 骨架；顶层 INDEX 与各 group `INDEX.md` 由 create/execute 维护（结构异于其他 INDEX，见 `plan-format.md`），track 只读。

## 4. INDEX.md（每个 docs 目录必备）

`docs/` 自身及其每个子目录都有一份 `INDEX.md`，登记该目录下所有文件（或子目录）的相对路径与一句话说明。

**模板与规则见 `skills/lib/index-format.md`（即 `../lib/index-format.md`）——执行时先 `read` 该文件。**

要点速览：

- **先索引后正文**：进入任何 `docs/` 目录先读 `INDEX.md`，再按需加载具体文件——禁止盲猜文件名。
- **同步维护**：文件增删时立即更新同级 `INDEX.md`。
- **粒度**：`docs/INDEX.md` 登记子目录；各子目录的 `INDEX.md` 登记其下具体文件。
- **特例**：`docs/plan/INDEX.md` 结构异于其他目录（分 active/completed 段、带状态列），格式见 `skills/lib/plan-format.md`「INDEX.md 结构」；本技能创建其骨架（两段空表），内容由计划系统维护。

## 5. 递归 CONTEXT.md（术语表）

`CONTEXT.md` 是术语表，固化项目通用语，消除人机用词歧义。**详细模板与规则见 `skills/lib/context-format.md`（即本技能目录的 `../lib/context-format.md`）——执行时先 `read` 该文件。**

要点速览：

- 单上下文：根级一份 `CONTEXT.md`；多上下文：根级 `CONTEXT.md`（共用术语）+ `CONTEXT-MAP.md` + 各模块 `CONTEXT.md`。
- 只写术语、要武断、定义紧凑、随用随写、不含实现细节。
- 多上下文时：跨上下文通用的术语归**根级** `CONTEXT.md`，专属术语归各模块 `CONTEXT.md`，不重复。

## 6. ADR（架构决策记录）

决策记录存于 `docs/adr/`。**格式、编号与「何时创建」的判断标准见 `skills/lib/adr-format.md`（即 `../lib/adr-format.md`）——执行时先 `read` 该文件。**

## 7. 完成标准

- 缺失的 `docs/{spec,generated,reference,adr}/` 均已创建，每个目录（含 `docs/` 自身）含 `INDEX.md`；`docs/plan/` 创建为含 `active/`、`completed/`、`INDEX.md` 骨架（两段空表）。
- `docs/INDEX.md` 已登记各子目录。
- 单上下文：根级存在 `CONTEXT.md`。多上下文：根级同时存在 `CONTEXT.md`（共用术语）与 `CONTEXT-MAP.md`。二者皆无时按单上下文初始化根级 `CONTEXT.md`。
- `docs/generated/` 若在版本控制下，写入 `.gitignore`，并保留其 `INDEX.md`。
- 向用户报告：新建/跳过了哪些路径、当前结构是单上下文还是多上下文。
