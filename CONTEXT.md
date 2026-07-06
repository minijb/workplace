# 计划系统（Planning System）

本上下文覆盖 `plan-create` / `plan-execute` / `plan-track` 三 skill 共享的计划文件格式与任务分解模型。边界：**如何把目标拆解成可执行的任务树、如何在文件系统中承载它、如何跟踪状态**。不含：具体的执行模式选型（react/subagent/hybrid 已有）、领域建模（归 grilling-with-context）。

## Scope

- **In**: 计划的文件/目录结构、任务的层级分解模型、节点角色与状态、计划索引（INDEX.md）的形态、跨文件依赖引用、归档规则。
- **Out**: 任务执行协议（react/subagent/hybrid，见 `plan-execute/references/modes.md`）、领域术语（归各自 `CONTEXT.md`）、docs 脚手架初始化（归 `docs-workspace`）。

## Language

### Plan Tree（计划树）

一个计划不再是单个 `.md` 文件，而是**镜像任务层级的文件/目录树**：每个节点是目录或文件，父子关系即任务分解关系。所有计划都是树——哪怕只有 1-2 个任务也是浅树（单文件格式已退役）。
- **Aliases**: 多文件计划、树状计划
- **Avoid**: 单文件计划（旧模型，仅用于描述历史/迁移）、flat plan
- **See also**: Group Node、Leaf Task、Plan Manifest、Dotted ID

### Plan Manifest（计划清单）

计划树根目录下的 `plan.md`，承载**计划级**结构化字段：`goal` / `references` / `constraints` / `acceptance` / `default_mode` / `status`（生命周期：draft|ready|in_progress|done|blocked|abandoned）。它是计划的身份与终态来源；任务树（INDEX.md + 各节点文件）与之分离。
- **See also**: Plan Tree、Archive

### Group Node（分组节点）

计划树中的**非叶节点**，按功能聚合若干子节点（Group 或 Leaf）。**不做实现、不可执行**——只承载分组与状态汇总。对应一个目录，目录内有本地 `INDEX.md` 列出直系子节点。
- **状态**：**派生（derived）**而非显式——见 Roll-up；只读，executor 不写 group 状态。
- **Avoid**: 大任务、子任务（相对词，角色不清）、Epic、Story（固定层语义包袱）
- **See also**: Leaf Task、Roll-up、Plan Tree

### Leaf Task（叶子任务）

计划树中的**原子可执行节点**，无子节点，是计划中**唯一可执行**的单位。保留旧 `T` 级任务语义：携带 `acceptance` / `verification` / `files` / `depends` / `status`（todo|in_progress|done|blocked，显式、executor 写）/ 可选 `mode` 覆盖。对应一个 `.md` 文件。
- **Avoid**: 大任务、子任务（相对词）、work package（WBS 用语，保留为别名）
- **Aliases**: work package
- **See also**: Group Node、Dotted ID、Plan Tree

### Dotted ID（点状标识）

反映树深度的层级编号，形如 `1` / `1.2` / `1.2.3`；每段对应该层子节点的有序位置（与 `01-`/`02-` 目录前缀对应）。**计划内唯一**。替代旧的扁平 `T1, T2`。每个节点在 frontmatter 声明权威 `id`；`depends` 引用 Dotted ID（叶或组；依赖一个组 = 其下叶子全 done）。**计划是封闭依赖图**——`depends` 只引用本计划内 ID，不跨计划。
- **See also**: Leaf Task、Group Node

### Roll-up（状态汇总）

Group Node 状态的派生规则，由子节点计算、只读：任一子 `blocked`→`blocked`；否则全 `done`→`done`；否则任一 `in_progress`→`in_progress`；否则 `todo`。executor 改叶子状态后向上刷新各祖先 group 的本地 INDEX 与计划根进度。
- **See also**: Group Node、Leaf Task

### Archive（归档）

**只有根计划**（整棵 Plan Tree）在 `plan.status: done`（所有叶子 done 且计划级 acceptance 满足）时，把**整个计划目录**从 `active/` 移到 `completed/`。Group 节点不单独归档；非 `done`（含 abandoned/blocked）一律留 `active/`。
- **See also**: Plan Manifest、Plan Tree

## Relationships

- 一个 **Plan** 是一棵 **Plan Tree** 的根；根是一个 **Group Node**，其目录下有 **Plan Manifest**（`plan.md`）与本地 `INDEX.md`。
- 一个 **Group Node** 包含零或多个 **Group Node** 与 **Leaf Task**；其状态由 **Roll-up** 从子节点派生。
- 一个 **Leaf Task** 无子节点，是计划中**唯一可执行**的节点；其状态显式由 executor 写。
- **Dotted ID** 的段数 = 节点深度；计划内唯一。
- 节点间依赖用 **Dotted ID** 引用，**仅在计划内**（封闭图）；依赖一个 group = 其下叶子全 done。
- 每层 group 目录有本地 `INDEX.md`（直系子节点 + 角色 + 状态 + 进度），自相似；顶层 `docs/plan/INDEX.md` 仍是扁平计划注册表，每行进度 = 叶子完成比。
- **Archive** 仅作用于根计划：全叶子 done 且 acceptance 满足 → 整个计划目录移入 `completed/`。

## Open Questions

（本轮盘问 Q1–Q7 已全部达成共识，结晶为上方术语与关系；难逆决策——多文件树状计划格式——拟入 ADR-0001，待用户确认是否落盘。）
