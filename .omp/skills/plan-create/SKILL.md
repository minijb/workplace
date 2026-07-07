---
name: plan-create
description: 规划系统的 Planner 阶段。接收一个目标或规格，先用 grilling-with-context 与用户逐题盘问、明确目标与领域模型（术语入 CONTEXT.md、决策入 docs/adr/），再做只读分析，把它拆解为一棵有序、可验证、带依赖与执行模式（react/subagent/hybrid）的任务树（group/leaf，多文件），写入 docs/plan/active/<slug>-<日期>/。在写任何代码前用它把目标变成结构化计划。不执行任务——执行归 plan-execute，进度查询归 plan-track。
---

# 计划系统 · 创建（Planner）

把"做什么"拆成"怎么做"。本 skill 是计划系统的**只读分析**阶段：扫描现状、把目标分解为一棵任务树（group/leaf）、定依赖、选默认执行模式，产出一个**计划目录**（多文件任务树）。**不写业务代码、不修改源码。**

> **三 skill 关系**：`plan-create`（本 skill，规划）→ `plan-execute`（按计划跑）→ `plan-track`（查进度）。三者共享 `skills/lib/plan-format.md` 这个文件格式契约——**操作任何计划前先 `read` 它**。
>
> **核心模型**：计划 = 镜像任务层级的文件/目录树。节点二元——**group**（目录，按功能分组、不可执行、状态派生）与 **leaf**（`.md` 文件，唯一可执行、状态显式）。节点用 **Dotted ID**（`1`/`1.2`/`1.2.3`）标识，依赖图计划内封闭。详见 `plan-format.md` 与根级 `CONTEXT.md`。

## 0. 前置：读契约

每次执行本 skill，先 `read skills/lib/plan-format.md`，确认目录布局、`plan:`/`task:` frontmatter 字段、Dotted ID 规则、状态/模式词表、两层 INDEX 结构。**禁止凭记忆写计划格式。**

> **引用基点约定**：本 skill 内出现的 `references/*` 一律指 `skills/plan-create/references/*`（相对 skill 目录，下同）；`skills/*` 指相对 skills 根。

## 1. 明确目标与约束（用 grilling-with-context 盘问）

入参是一句话目标或一份规格（PRD / issue / spec）。**读完契约后，先用 `grilling-with-context` skill 与用户确认细节、明确目标**：`read skills/grilling-with-context/SKILL.md` 并按其协议逐题盘问（一次一题、给出你推荐的答案、走遍设计树每个分支），边盘问边把结晶的术语写进 `CONTEXT.md`、难逆决策写进 `docs/adr/`、未决项写进 Open Questions。**目标是在动笔分解任务前，与用户就「做什么、达成什么」达成共识，并让领域模型比会话开始时更清晰。** 能查代码回答的别问用户——grilling 与 §2 都遵循此原则。**grilling 深度随目标清晰度缩放**：目标极清晰（如给既有模块加一个明确开关）时，可只做轻量确认，无需强制全套盘问 + 落盘 `CONTEXT.md`/ADR；目标越模糊，盘问越深。

盘问须澄清并产出以下五项——它们是写计划的必需输入：

- **goal**（一句话目标）：做什么 + 达成什么（不是怎么做）。
- **references**（相关 PRD / issue / spec / **ADR**）：分条列出，每条用关键词标签表明它对计划的作用（标签见 `plan-format.md`「参考标签词表」，frontmatter 存为小写）：
  - `[IMPORTANT]`——核心/必读，直接决定目标成败。
  - `[REFER]`——参考，提供模式/约定/历史决策。
  - `[CONTEXT]`——背景，只解释为什么做。
  - `[BLOCKER]`——阻塞项，含未决决策或外部依赖，定稿前需先解决。
  - 一条资料可挂多个标签；链接优于粘贴。
- **constraints**（硬约束）：不可逆操作、停机窗口、合规、版本兼容——执行时不得违反的红线。
- **预计触碰文件**：分条列出预期会修改或新建的文件，每条后简述原因/作用。§2 扫描前是初判，§3 分解后落实为各 leaf 的 `files`。最终写入 `plan.md` 的「预计触碰文件」段。**初判仅草稿；§3 后以各 leaf `files` 的并集覆写正文段，初判不保留**——避免初判与最终并集 drift。
- **acceptance**（计划级验收）：计划算"完成"的可观察条件——具体到能跑命令或能点开的检查。全部叶子 done 不等于计划 done，必须满足此项。

> 盘问结晶物按下列映射进计划：ADR / spec → `references`（关键决策标 `[IMPORTANT]`）；`CONTEXT.md` 术语 → 计划正文用规范术语；Open Questions → `[BLOCKER]` reference 或「风险与缓解」段。grilling 已写入 docs 的产物，本 skill 不重复写。

目标运行时才明确、需要边做边探索 → `default_mode` 倾向 `react`。详见 §4 与 `references/mode-selection.md`。

### 盘问收敛失败处置

盘问后若目标仍**过宽或不可分解**（写不出可测 `acceptance`、或一个计划装不下整段目标），不要硬拆。按下列**三出口**择一处置：

1. **缩小范围**：把过宽目标收窄为一个**可测子目标**，`plan.md` 背景段说明缩小理由，原目标记入「风险与缓解」段或下一计划的输入。
2. **拆为前置计划**：把「先探索 / 先建工具 / 先做地基」独立成一个**前置 plan**，当前目标延后到该前置完成后。
3. **标 `draft` + `[BLOCKER]`**：确实无法收敛时，`plan.status: draft`，把未决范围问题作为 `[BLOCKER]` reference 登记进「风险与缓解」段，显式交还用户。

> 范例形态：`plan.status: draft` + 背景段说明缩小理由 + 风险段登记「原目标被缩小」。

## 2. 只读扫描现状

写任务前，**只读**地建立分解所需的现状心智模型（不修改任何文件）。领域模型与术语已在 §1 盘问中建立，本步聚焦分解信号——callsite、既有计划、可复用模式：

- `glob` 项目结构，定位相关源码目录。
- `grep` / `read` 关键模块，识别现有模式与约定（**复用既有约定，禁止另起一套**）。
- `lsp references` 在改导出符号前查 callsite，避免漏改。
- 留意既有计划：**先读顶层 `docs/plan/INDEX.md`**，再读相关计划**目录**的 `INDEX.md`（`active/` 与 `completed/` 都看）。计划现在是目录树，不是单文件。

把发现写进 `plan.md` 的「背景」段——给六个月后的自己看。

**无业务源码时退化**：纯规格 / 纯文档规划（早期项目只有 PRD 未写码，或本仓库这类「改 `.md` 指令」的 skill 规划）时，§2 的 `glob`/`grep`/`lsp` 三项会悬空——直接跳过，并在 `plan.md` 背景段注明「无业务源码，依赖外部仓库或为新建」。

## 3. 分解任务（group/leaf 树）

把目标拆为一棵有序、可独立验证的任务树。**分解策略与任务尺寸标准见 `references/decomposition.md`——分解前先 `read` 它。** 要点：

- **按功能分组成树**：用一个 **group** 聚合一段端到端功能（垂直切片），group 内再分 group 或 leaf。"建全部 schema"是坏的横向铺层；"建用户表+注册 API+注册 UI"是一个好的功能 group。
- **MECE**：兄弟节点间相互独立、合起来完全穷尽父节点的目标。
- **leaf 是唯一可执行单位**：尺寸控制（触碰 ≤5 文件、一次专注会话内完成）；超过就继续拆成 group + 子 leaf。
- **每 leaf 必备字段**：`acceptance`（具体可测）、`verification`（可执行命令）、`depends`（Dotted ID 列表）、`files`（预计触碰面）。group **不**携带这些字段。
- **Dotted ID**：节点命名 `<NN>-<kebab>`，`<NN>` = ID 末段；路径决定 ID（`01-session/02-iface.md` → `1.2`）；直挂根的 leaf 取单段（`01-foo.md` → `id="1"`）。

## 4. 选默认执行模式

依据目标特性，为 `default_mode` 选 `react` / `subagent` / `hybrid`。**决策树与权衡见 `references/mode-selection.md`——选模式前先 `read` 它。** 速览：

| 场景 | default_mode |
|---|---|
| 任务耦合紧、需上下文连续、调试或探索类 | `react` |
| 任务相互独立、规模大、需领域专长 | `subagent` |
| 耦合与独立并存（多数真实计划） | `hybrid`（默认首选） |

`default_mode` 写入 `plan.md`。leaf 级 `mode` 仅在与默认**显著不同**时才写。**group 无 mode**（不可执行）。

## 5. 排依赖与设检查点

- **依赖图**：把 `depends` 关系画成 mermaid `flowchart`（节点 ≥4 或依赖非平凡时），节点用 **Dotted ID**。拓扑序 = 实现序；环依赖必须解开（拆节点或重新分解）。`depends` 可引用 leaf 或 group；依赖一个 group = 其下叶子全 done。
- **检查点**：每 2-4 个 leaf 一个 checkpoint，写入 `plan.md`「检查点」段。executor 到达边界时暂停跑验证。
- leaf ≤3 的简单线性计划设 **1 个收尾 checkpoint** 即可；checkpoint 标题用叶末 ID（如「1-2 完成」），无 group 时不用「N.*」。

## 6. 自检（Plan-Validate）

写完计划，**对照真相源**自检：

- 每个 leaf 的 `id` 与路径序号一致；每个 `depends` 的 Dotted ID 存在于本计划；无环；前置未全 done 的不会被先调度。
- 每个 leaf 的 `files` 路径在仓库中存在或明确是新建（`glob` 确认）。
- 每个 leaf 的 `verification` 真实可跑：**代码 leaf** 复制命令到 bash 验一次，或确认脚本存在；**文档/指令 leaf**（如本仓库改 `.md` 的 skill）可用 `grep` 校验关键内容存在，或声明「手动遵循指令跑一次」——两类都算合格。
- 每个 leaf 的 `acceptance` 可观察（"性能更好"不算；"p99 < 200ms"算）。
- 每个 leaf 触碰 ≤5 文件；超尺寸的回到 §3 继续拆。
- group 目录都有 `INDEX.md`，列出全部直系子节点；派生状态行已初始化。
- `plan.md`「预计触碰文件」段 = 各 leaf `files` 的并集；`references` 中 `[BLOCKER]` 项已在风险段登记或已解决。

自检不通过，回到对应步骤修，**不要带着已知缺陷交付 ready**。

## 7. 写文件

按 `plan-format.md` 的结构写到 `docs/plan/active/<slug>-<YYYYMMDD>/`：

- `plan.md`：`plan:` frontmatter（`status: draft`，自检通过后改 `ready`；`default_mode`；`created`/`updated` 当天）+ 正文（背景、依赖图、检查点、预计触碰文件、风险与缓解、复盘笔记）。
- 根 `INDEX.md`：根 group 的直系子节点表 + 派生状态行。
- 每个 group 子目录：`<NN>-<kebab>/` + 其 `INDEX.md`（递归，自相似）。
- 每个 leaf：`<NN>-<kebab>.md`，含 `task:` frontmatter。
- **写完即更新顶层 `docs/plan/INDEX.md`**：「进行中（active/）」段加一行（路径指向**计划目录**、标题、状态、进度 0/N、模式、更新日）。
- 若 `docs/plan/active/` 不存在，先用 `docs-workspace` skill 初始化（本 skill 不负责建目录骨架）。

## 8. 完成标准

- 计划目录存在于 `docs/plan/active/<slug>-<date>/`，含 `plan.md` + 根 `INDEX.md` + 节点树；frontmatter 与字段严格符合 `plan-format.md`。
- `plan.status` 为 `ready`（自检通过）或显式 `draft`（**自检不通过，或目标层面未定型**——标注缺什么 / 缺哪个决定；见 §1「盘问收敛失败处置」）。
- 每个 leaf 有 `id`（与路径一致）+ `acceptance` + `verification` + `depends` + `files`。
- 每个 group 目录有 `INDEX.md`；依赖图无环、无悬空 Dotted ID；检查点已设。
- §1 盘问产出的五项已落入对应位置：`goal`/`references`/`constraints`/`acceptance` 进 `plan.md` frontmatter，预计触碰文件进正文段（无相关资料时 `references` 可为空数组）。
- `default_mode` 已选并可在 `mode-selection.md` 的决策树中找到依据。
- 向用户报告：计划目录路径、leaf 数与 group 数、默认模式及理由、识别到的风险。

## 不做什么

- 不执行任务、不改源码——那是 `plan-execute`。
- 不查询进度——那是 `plan-track`。
- 不创建 `docs/` 目录骨架——那是 `docs-workspace`。
- 不移动计划目录到 `completed/`、不置终态——计划归档（`done` 时移整个目录、挪 INDEX 行）是 `plan-execute` 的职责；本 skill 只在 `active/` 创建并往顶层 INDEX「进行中」段加行。
