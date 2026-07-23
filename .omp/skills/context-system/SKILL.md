---
name: context-system
description: 管理限界上下文的术语表 CONTEXT.md——用模板创建（模块级/项目级）、用 Python 脚本校验与查询、派生 JSON 索引。当用户要新建/校验/查询 CONTEXT.md 术语表，或管理单/多上下文术语对齐时使用。CONTEXT.md 是真源（人或 AI agent 直接写），JSON 由脚本派生（不手改）。本 skill 独立自包含，不依赖其他 skill。
---

# Context System（上下文术语管理）

管理限界上下文的**术语表 `CONTEXT.md`**：用模板创建、用脚本校验与查询、派生 JSON 索引。CONTEXT.md 用于在人与人、人与 LLM 之间对齐通用语（ubiquitous language）——只描述概念**是什么**，不描述如何实现。

## 核心模型

- **真源**：`CONTEXT.md`（Markdown，人或 AI agent 直接写）。
- **派生**：JSON（由脚本从 CONTEXT.md 解析生成，用于查询/校验，**不手改**）。
- **数据流**：写 CONTEXT.md → 脚本解析 → JSON 索引 → 校验/查询。

## 0. 前置

- 确认 Python 3.8+ 可用（脚本仅用标准库，无第三方依赖）。
- 判断单上下文 vs 多上下文：仓库内有多个相互独立、各自具备完整领域语义的模块（如 `src/ordering`、`src/billing`）为**多上下文**；仅是分层（`controllers/services`）仍属**单上下文**。无法判断时询问用户。
- 本 skill 独立运行，不依赖其他 skill。

## 1. 创建 CONTEXT.md

按上下文形态选模板（执行时先 `read` 对应模板）：

- **单上下文**（多数仓库）：根目录一份 `CONTEXT.md`，用**模块级模板**。
- **多上下文**（monorepo / 多模块）：根目录一份**项目级** `CONTEXT.md`（跨上下文通用术语）+ 一份 `CONTEXT-MAP.md`（上下文清单），每个上下文目录各一份**模块级** `CONTEXT.md`。

模板：
- 模块级：`./references/context-template-module.md`——创建模块级 CONTEXT.md 前先 `read`。
- 项目级：`./references/context-template-project.md`——创建项目级共用 CONTEXT.md 前先 `read`。

**字段分层**（模板内逐项标注）：
- **核心层（必填，保持轻量）**：术语名 + 定义 + Aliases + Avoid + Example + See also。
- **扩展层（可选，整段可省略）**：Status（draft/active/deprecated）、Source（出处）；另可选 Owner、Since、Anti-example。

**术语规则**：
- 只写本上下文特有的概念；通用编程概念（超时、错误类型）不入内。加词前自问：这是本上下文独有的概念吗？
- 要武断：同一概念多词时选一个作主词，其余入 `Aliases` 或 `Avoid`。
- 定义紧凑：每个术语一两句话，说清「是什么」而非「做什么」。
- 随用随写：术语被确定时**立即**更新，不积压；文件仅在首个术语确立时创建。
- 不含实现：不写技术选型、数据结构、接口签名。
- 术语只归一处：跨上下文通用的归**项目级**，仅属某上下文的归**该模块级**；不重复定义，必要时用 `See also` 互链。
- 不要为凑模板杜撰术语——CONTEXT.md 可只含标题与一两句说明。

## 2. 校验（质量检查）

```bash
# 校验单个 CONTEXT.md
python3 .omp/skills/context-system/scripts/context_manager.py validate path/to/CONTEXT.md
# 校验整个仓库所有 CONTEXT.md
python3 .omp/skills/context-system/scripts/context_manager.py validate .
```

校验项：术语重复、悬空 `See also`（引用的术语不存在）、缺定义、`Status` 取值非法、`Aliases` 与某术语主词冲突、缺一级标题。

校验不通过 → 修正 CONTEXT.md（真源），再跑。

## 3. 查询与派生 JSON

```bash
# 解析 CONTEXT.md → JSON（派生索引）
python3 .omp/skills/context-system/scripts/context_manager.py parse path/to/CONTEXT.md -o context.json

# 查询：按关键词
python3 .omp/skills/context-system/scripts/context_manager.py query path/to/CONTEXT.md "订单"
# 查询：按状态
python3 .omp/skills/context-system/scripts/context_manager.py query path/to/CONTEXT.md --status deprecated

# 多上下文：汇总各模块生成 CONTEXT-MAP.md
python3 .omp/skills/context-system/scripts/context_manager.py generate-map . -o CONTEXT-MAP.md
```

JSON 结构见 `./references/json-schema.md`——需要理解派生数据结构时先 `read`。**JSON 是派生产物，不要手改**；要改术语就改 CONTEXT.md 再重新 `parse`。

## 收敛

- 创建/修改 CONTEXT.md 后，跑一次 `validate` 确保无悬空/重复。
- 多上下文项目：各模块 CONTEXT.md 就位后，用 `generate-map` 生成 CONTEXT-MAP.md。

## 完成标准

- CONTEXT.md 遵循模板结构，字段分层正确（核心必填、扩展可选）。
- `validate` 通过：无重复术语、无悬空 See also、无缺定义、Status 合法。
- 如需索引，已 `parse` 出 JSON 且与 CONTEXT.md 一致（JSON 未手改）。

## 不做什么

- **不写实现细节**：技术选型、数据结构、接口签名不进 CONTEXT.md（归规格或决策文档）。
- **不手改 JSON**：JSON 是派生产物；改术语就改 CONTEXT.md 再 `parse`。
- **不替领域做决策**：CONTEXT.md 记录已达成共识的术语；领域决策本身不在本 skill 范围。
- **不实现/不执行任务**：本 skill 只管术语表的创建、校验与查询。
