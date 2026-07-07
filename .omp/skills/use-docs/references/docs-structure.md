# docs/ 工作区结构

`docs/` 工作区的完整结构总图与每个目录 / 文件的作用、边界、格式契约位置。本文件是 `use-docs` skill 的结构附录，**只读、只解释**——搭建归 `docs-workspace`，确切格式见 `skills/lib/`。

## 适用范围

供需要对照 `docs/` 树中某个目录或文件「是什么、装什么、不装什么、格式在哪」时查阅。术语表（`CONTEXT.md` / `CONTEXT-MAP.md`）单独见 `./context-structure.md`。

## 完整树

```
项目根
├── CONTEXT.md                    # 术语表（单上下文放这里）；解剖见 ./context-structure.md
├── CONTEXT-MAP.md                # 仅多上下文：上下文清单与关系
├── docs/
│   ├── INDEX.md                  # 登记各子目录
│   ├── spec/        INDEX.md     # 功能规格
│   ├── generated/   INDEX.md     # 自动生成产物（建议 gitignore）
│   ├── reference/   INDEX.md     # 外部知识
│   ├── adr/         INDEX.md     # 架构决策 NNNN-slug.md
│   └── plan/
│       ├── INDEX.md              # 计划注册表（结构异于其他 INDEX）
│       ├── active/               # 非终态计划（draft/ready/in_progress/blocked/abandoned）
│       └── completed/            # 仅 status: done
└── src/  …                       # 多上下文时各模块内放 CONTEXT.md
```

格式契约不在 `docs/` 内，而在 skills 层——它们是 docs 各文件的「写法说明书」。**现有契约请 `read skills/lib/` 目录获取**（不静态列举，避免 lib 增删时此处漂移）；当前覆盖 CONTEXT / INDEX / ADR / plan 各自的 `*-format.md`。

> 规则：docs 文件的**内容**（规格、决策、术语）放 `docs/`；这些文件的**写法契约**放 `skills/lib/`。use-docs 只指路，不重述契约。

## 逐项说明

每行：**是什么** · **装什么** · **不装什么（→ 该去哪）** · **格式契约**。

### `docs/` — 总入口

- **是**：项目级知识数据的总入口，承载跨团队共享的长期记忆。
- **装**：下列所有子目录与 `docs/INDEX.md`。
- **不装**：术语表（→ 根级 `CONTEXT.md`）、源码、构建产物。
- **契约**：目录职责见 `docs-workspace`；子目录登记格式见 `index-format.md`。

### `docs/INDEX.md` — 子目录登记

- **是**：`docs/` 自身的目录页，登记各**子目录**的相对路径与一句话说明。
- **装**：`./spec/`、`./generated/`、`./reference/`、`./adr/`、`./plan/` 各一行。
- **不装**：具体文件（→ 进各子目录的 INDEX）；术语（→ CONTEXT.md）。
- **契约**：`skills/lib/index-format.md`（登记子目录的示例）。
- **纪律**：子目录增删时同步更新本文件。

### `docs/spec/` — 功能规格

- **是**：功能的「做什么、达成什么」定义：PRD、需求清单、接口约定、验收标准。
- **装**：需求、验收标准、接口契约、行为规格。
- **不装**：术语定义（→ CONTEXT.md）、架构决策的「为什么」（→ `adr/`）、第三方 API 摘要（→ `reference/`）、执行计划（→ `plan/`）。
- **契约**：无独立 lib 契约（自由格式）；需 INDEX 登记，见 `index-format.md`。

### `docs/generated/` — 自动生成产物

- **是**：工具 / agent 生成的产物：分析报告、迁移计划、审计输出。
- **装**：机器生成的、可重新生成的报告。
- **不装**：人写的长期知识（→ `spec/` / `adr/` / `reference/`）。
- **契约**：建议加入 `.gitignore`，但 `INDEX.md` 仍维护（供 agent 当次会话定位）；见 `index-format.md`。

### `docs/reference/` — 外部知识

- **是**：外部世界的知识引用：第三方 API 摘要、标准 / 规范引用、调研笔记。
- **装**：外部依赖、规范、调研的引用与摘要。
- **不装**：本项目的功能规格（→ `spec/`）、本项目的决策（→ `adr/`）。
- **契约**：无独立 lib 契约；需 INDEX 登记，见 `index-format.md`。

### `docs/adr/` — 架构决策记录

- **是**：难以回退、需要背景、经过真实权衡的决策记录，文件名 `NNNN-slug.md`。
- **装**：架构形态、集成方式、带锁定的技术选型、边界与范围、被否决的备选、代码中不可见的约束。
- **不装**：容易回退的改动（直接改即可）、不令人困惑的显然决定、没有备选的「做了显然的事」、术语（→ CONTEXT.md）。
- **契约**：`skills/lib/adr-format.md`（模板、编号规则、三条「何时创建」标准）。
- **何时写**：仅当「难以回退 + 无背景会困惑 + 真实权衡」三者**同时**成立。

### `docs/plan/` — 计划系统托管

- **是**：执行计划的唯一持久状态，由三个 skill 托管：`plan-create` 写入、`plan-execute` 推进、`plan-track` 只读汇总。本 skill **只解释结构，不读写计划**。
- **装**：顶层 `INDEX.md`（注册表）、`active/`、`completed/`。一个计划是 `active/`（或 `completed/`）下的**一个目录**——一棵任务树（group 目录 + leaf `.md` 文件），含 `plan.md`（计划级 frontmatter）与各级 group 的 `INDEX.md`。
- **不装**：非计划内容（规格 → `spec/`，决策 → `adr/`）。
- **契约**：`skills/lib/plan-format.md`（核心模型、`plan:`/`task:` frontmatter、Dotted ID、状态 / 模式词表、roll-up、两层 INDEX 结构）。

### `docs/plan/INDEX.md` — 计划注册表（结构特例）

- **是**：计划系统的注册表与轻量看板，**结构异于**其他 INDEX：分「进行中（active/）」与「已完成（completed/）」两段，带状态 / 进度 / 模式列。**路径指向计划目录**（非文件），进度 = 叶子完成比。
- **装**：每个计划一行（目录路径、标题、状态、进度、模式、更新日）。
- **不装**：计划内容（→ 各计划目录内的 `plan.md` 与任务树）；非计划目录的内容。
- **契约**：`skills/lib/plan-format.md` 的「INDEX.md 结构」段（**不是** `index-format.md`）。
- **状态真源**：各计划 `plan.md` 的 `plan.status` 才是真源；顶层 INDEX 只是看板，`plan-track` 负责遍历树对账纠偏。

### 每个 group 目录的 `INDEX.md` — 本地子节点表

- **是**：计划树自相似的一环。每个 group 目录（含计划根目录）各有一份 `INDEX.md`，列出**直系**子节点（id / 路径 / 角色 group|leaf / 状态 / 进度）+ 该 group 的派生状态（roll-up，只读）。
- **契约**：`skills/lib/plan-format.md`「INDEX.md 结构 → 每个 group 目录的 INDEX.md」。

### `docs/plan/active/` 与 `docs/plan/completed/`

- **`active/`**：非终态计划——`draft`、`ready`、`in_progress`、`blocked`、`abandoned` 都留这里（`blocked` 需人介入、`abandoned` 留作复盘，都不算完成）。
- **`completed/`**：仅 `plan.status: done` 的计划。executor 置 `done` 时把**整个计划目录**从 `active/` 移到此处，并把顶层 INDEX 该行从「进行中」段挪到「已完成」段。
- **契约**：计划目录命名 `<slug>-<YYYYMMDD>/`，桶与状态对应见 `plan-format.md`「生命周期」。

## INDEX.md 通用纪律（所有 docs 目录）

INDEX 通用纪律（先索引后正文 / 同步维护 / 粒度 / 相对路径）见 `skills/lib/index-format.md#规则`。`docs/plan/INDEX.md` 是结构特例，见 `skills/lib/plan-format.md`「INDEX.md 结构」。
