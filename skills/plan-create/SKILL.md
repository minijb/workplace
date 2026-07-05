---
name: plan-create
description: 规划系统的 Planner 阶段。接收一个目标或规格，做只读分析，把它拆解为有序、可验证、带依赖与执行模式（react/subagent/hybrid）的任务计划，写入 docs/plan/<slug>-<日期>.md。在写任何代码前用它把目标变成结构化计划。不执行任务——执行归 plan-execute，进度查询归 plan-track。
---

# 计划系统 · 创建（Planner）

把"做什么"拆成"怎么做"。本 skill 是计划系统的**只读分析**阶段：扫描现状、分解任务、定依赖、选默认执行模式，产出一份结构化计划文件。**不写业务代码、不修改源码。**

> **三 skill 关系**：`plan-create`（本 skill，规划）→ `plan-execute`（按计划跑）→ `plan-track`（查进度）。三者共享 `skills/lib/plan-format.md` 这个文件格式契约——**操作任何计划前先 `read` 它**。

## 0. 前置：读契约

每次执行本 skill，先 `read skills/lib/plan-format.md`，确认文件位置、frontmatter 字段、任务字段、状态/模式词表。**禁止凭记忆写计划格式。**

## 1. 明确目标与约束

入参是一句话目标或一份规格（PRD / issue / spec）。先澄清：

- **goal**：一句话，做什么 + 达成什么（非怎么做）。模糊则向用户追问，不要替用户决定方向。
- **constraints**：硬约束（不可逆操作、停机窗口、合规、版本兼容）。问不出就留空数组。
- **acceptance**（计划级）：计划算"完成"的可观察条件——具体到能跑命令或能点开的检查。

目标运行时才明确、需要边做边探索 → 在 `default_mode` 倾向 `react`。详见 §4 与 `references/mode-selection.md`。

## 2. 只读扫描现状

写任务前，**只读**地建立现状心智模型（不修改任何文件）：

- `glob` 项目结构，定位相关源码目录。
- `grep` / `read` 关键模块，识别现有模式与约定（**复用既有约定，禁止另起一套**）。
- `lsp references` 在改导出符号前查 callsite，避免漏改。
- 留意：是否多模块（影响是否多上下文）、是否有现成抽象可复用、是否已存在 `docs/plan/` 下相关计划。

把发现写进计划的「背景」段——给六个月后的自己看。

## 3. 分解任务

把目标拆为有序、可独立验证的任务。**分解策略与任务尺寸标准见 `references/decomposition.md`——分解前先 `read` 它。** 要点：

- **垂直切片**：每个任务端到端交付一段可测功能，而非横向铺一层（"建全部 schema"是坏的；"建用户表+注册 API+注册 UI"是好的）。
- **MECE**：任务间相互独立、合起来完全穷尽目标。
- **尺寸**：单任务触碰 ≤5 文件、能在一次专注会话内完成。否则继续拆。
- **每任务必备字段**：`acceptance`（具体可测）、`verification`（可执行命令）、`depends`（前置任务 id）、`files`（预计触碰面）。

任务编号 `T1, T2, ...`，与 `depends` 引用一致。

## 4. 选默认执行模式

依据目标特性，为 `default_mode` 选 `react` / `subagent` / `hybrid`。**决策树与权衡见 `references/mode-selection.md`——选模式前先 `read` 它。** 速览：

| 场景 | default_mode |
|---|---|
| 任务耦合紧、需上下文连续、调试或探索类 | `react` |
| 任务相互独立、规模大、需领域专长 | `subagent` |
| 耦合与独立并存（多数真实计划） | `hybrid`（默认首选） |

任务级 `mode` 仅在与默认**显著不同**时才写（如默认 `hybrid`，但某调试任务标 `react`）。

## 5. 排依赖与设检查点

- **依赖图**：把 `depends` 关系画成 mermaid `flowchart`（任务 ≥4 或依赖非平凡时）。拓扑序 = 实现序；环依赖必须解开（拆任务或重新分解）。
- **检查点**：每 2-4 个任务一个 checkpoint，列出该阶段必须通过的验证。检查点是 executor 的暂停点，不是装饰。

## 6. 自检（Plan-Validate）

写完计划，**对照真相源**自检（这是 Plan-Validate-Execute 模式中的 Validate）：

- 每个 `depends` id 都存在；无环；前置未全 `done` 的任务不会被先调度。
- 每个 `files` 路径在仓库中存在或明确是新建（用 `glob` 确认）。
- `verification` 命令真实可跑（复制粘贴到 bash 验证一次，或确认脚本存在）。
- `acceptance` 是可观察的（"性能更好"不算；"p99 < 200ms"算）。
- 任务尺寸全部 ≤5 文件；超尺寸的回到 §3 继续拆。

自检不通过的，回到对应步骤修，**不要带着已知缺陷交付 ready**。

## 7. 写文件

按 `skills/lib/plan-format.md` 的结构写到 `docs/plan/<slug>-<YYYYMMDD>.md`：

- frontmatter：`status: draft`（自检通过后改 `ready`）、`default_mode`、`created`/`updated` 当天。
- 正文：背景、依赖图、任务清单、检查点、风险与缓解。
- 若 `docs/plan/` 不存在，先用 `docs-workspace` skill 初始化（本 skill 不负责建目录结构）。

## 8. 完成标准

- 计划文件存在于 `docs/plan/`，frontmatter 与任务字段严格符合 `plan-format.md`。
- `status` 为 `ready`（自检通过）或显式 `draft`（标注缺什么）。
- 每个任务有 `acceptance` + `verification` + `depends` + `files`。
- 依赖图无环、无悬空 id；检查点已设。
- `default_mode` 已选并可在 `mode-selection.md` 的决策树中找到依据。
- 向用户报告：计划路径、任务数、默认模式及理由、识别到的风险。

## 不做什么

- 不执行任务、不改源码——那是 `plan-execute`。
- 不查询进度——那是 `plan-track`。
- 不创建 `docs/` 目录结构——那是 `docs-workspace`。
- 不在 `docs/plan/` 建 `INDEX.md`——发现机制是扫 `*.md` 读 frontmatter（见 plan-track）。
