# Plan 文件格式（计划系统共享契约）

`plan-create`、`plan-execute`、`plan-track` 三个 skill 共用本格式。计划是计划系统的**唯一持久状态**：planner 写入它、executor 读写它（推进状态）、tracker 只读它。三者都**必须先读本文件**再操作任何计划。

> 术语定义（计划树、group、leaf、Dotted ID、roll-up、归档）见根级 `CONTEXT.md`「计划系统」上下文。本文件只规定**文件格式**。

## 核心模型：计划 = 任务树

一个计划不再是单个 `.md`，而是**镜像任务层级的文件/目录树**。节点二元角色：

- **group**（分组节点）= **目录**，按功能聚合子节点；**不可执行**；状态**派生**（roll-up，只读）。
- **leaf**（叶子任务）= **`.md` 文件**，计划中**唯一可执行**的单位；状态**显式**。

节点用 **Dotted ID**（`1`、`1.2`、`1.2.3`）标识，计划内唯一，段数=深度。依赖图**计划内封闭**——`depends` 只引用本计划内 ID。

## 存放位置

```
docs/plan/
├── INDEX.md                            # 扁平计划注册表（active/completed 两段）
├── active/
│   └── <slug>-<YYYYMMDD>/              # 一个计划 = 一个目录（根 group）
│       ├── plan.md                     # 计划级 frontmatter（plan: 块）+ 正文
│       ├── INDEX.md                    # 根 group 的直系子节点表 + 派生状态
│       ├── <NN>-<kebab>/               # group 子目录（按功能）
│       │   ├── INDEX.md                # 该 group 的直系子节点表
│       │   ├── <NN>-<kebab>.md         # leaf 任务文件
│       │   └── <NN>-<kebab>/           # 可继续嵌套（以此类推）
│       └── <NN>-<kebab>.md             # leaf 任务文件（直挂根）
└── completed/
    └── <slug>-<YYYYMMDD>/              # done 时整个计划目录移入此处
```

- `docs/plan/`（含 `active/`、`completed/`、顶层 `INDEX.md` 骨架）由 `docs-workspace` 创建；计划内容由本系统写入。
- `<slug>`：kebab-case 目标标识（如 `auth-jwt-migration`）；`<YYYYMMDD>`：创建日；`<NN>`：两位零填充序号 = Dotted ID 的**末段**。
- **节点命名一律 `<NN>-<kebab>`**（目录或文件）；`<NN>` 决定排序，也决定 ID 段。根计划目录例外，命名为 `<slug>-<YYYYMMDD>`。
- 路径 → ID 的换算：从根目录起，每进入一个 `<NN>-` 子节点追加一段。例 `…/01-session-abstraction/02-cookie-adapter.md` 的 id = `1.2`。
- 例：`docs/plan/active/auth-jwt-migration-20260705/`。

### 生命周期（谁移动什么）

| 阶段 | 动作 | 落点 |
|---|---|---|
| `plan-create` | 新建计划 | 在 `active/<slug>-<date>/` 写 `plan.md` + 根 `INDEX.md` + 各节点；顶层 `INDEX.md`「进行中」段加一行 |
| `plan-execute` | 推进 leaf 状态、刷新 roll-up、刷新 `updated` | 留 `active/`；同步刷新顶层 INDEX 该行（状态/进度/更新日）与各祖先 group `INDEX.md` 的派生状态行 |
| `plan-execute` | 置 `plan.status: done` | **移动整个计划目录**到 `completed/`；顶层 INDEX 该行从「进行中」挪到「已完成」 |
| `plan-track` | 只读汇总 | 先读顶层 `INDEX.md`，再扫实际目录对账纠偏（detect drift） |

桶与 `plan.status` 的对应（**仅 `done` 归档**）：

| 桶 | 容纳的 `plan.status` |
|---|---|
| `active/` | `draft`、`ready`、`in_progress`、`blocked`、`abandoned` |
| `completed/` | `done` |

> `abandoned`/`blocked` 不算完成，留 `active/`——INDEX 状态列会标出，避免误读为活跃。

## INDEX.md 结构（两层）

### 顶层 `docs/plan/INDEX.md` — 扁平计划注册表

形态仍是两段表，但**路径指向计划目录**（非文件），**进度 = 叶子完成比**。由 create/execute 维护，track 只读并对账。

```md
# 计划索引

docs/plan/ 的注册表。进入本目录先读此文件，再按需加载具体计划目录。
新增/移动/完成计划时同步更新本文件；状态以各计划 plan.md frontmatter 为真源。

路径指向计划目录（一棵任务树）；进入目录先读其 INDEX.md。进度 = 叶子完成比。

## 进行中（active/）
| 路径 | 标题 | 状态 | 进度 | 模式 | 更新 |
|---|---|---|---|---|---|
| `./active/auth-jwt-migration-20260705/` | 把会话认证从 cookie 迁移到 JWT | in_progress | 1/2 | hybrid | 2026-07-05 |

## 已完成（completed/）
| 路径 | 标题 | 完成日 | 结果 |
|---|---|---|---|
| `./completed/refactor-checkout-20260620/` | 重构结算模块 | 2026-06-22 | p99 降至 180ms |
```

### 每个 group 目录的 `INDEX.md` — 本地子节点表

**自相似**：每个 group 目录（含计划根目录）都有一份 `INDEX.md`，列出**直系**子节点 + 派生状态。group 自身**无 frontmatter**（角色=目录即隐式 group；id=路径序号；状态=派生不存储）。

```md
# 1 · 会话抽象层

{可选：该 group 为什么这样分组。}

> 派生状态：in_progress（1/2 叶子 done）

| ID | 节点 | 角色 | 状态 | 进度 |
|---|---|---|---|---|
| 1.1 | [01-iface](./01-iface.md) | leaf | done | — |
| 1.2 | [02-cookie-adapter](./02-cookie-adapter.md) | leaf | in_progress | — |
| 1.3 | [03-subsystem](./03-subsystem/) | group | todo | 0/1 |
```

- **进度**：leaf 填 `—`；group 填 `done 叶子数 / 总叶子数`。
- **派生状态**：由子节点 roll-up 计算（规则见「状态词表」），executor 改 leaf 状态后刷新本行。

## 文件结构

### `plan.md` — 计划级 frontmatter + 正文

```md
---
plan:
  id: auth-jwt-migration-20260705      # 与目录名（去 /）一致，全局唯一
  title: 把会话认证从 cookie 迁移到 JWT
  goal: >-                              # 一句话目标：做什么、达成什么
    所有受保护端点改用 Bearer JWT；旧 cookie 路径在一个版本后下线
  references:                           # 相关 PRD/issue/spec/ADR，打标签；见「参考标签词表」
    - tag: [important]                  # important|refer|context|blocker（YAML 列表，可多选）
      type: prd                         # prd|issue|spec|adr|doc
      title: 用户认证 PRD v2
      url: docs/prd/auth-v2.md          # 仓库路径或 URL
  status: in_progress                   # 见「状态词表」
  default_mode: hybrid                  # 见「模式词表」——planner 决定，可被单 leaf 覆盖
  created: 2026-07-05
  updated: 2026-07-05                   # executor 每次推进 leaf 状态时刷新
  replan_count: 0                      # executor 每次局部 replan 自增；≥3 未收敛→blocked（见 plan-execute/references/replan.md §4）
  constraints:                          # 计划级硬约束；executor 不得违反
    - 鉴权中断不超过 5 分钟
  acceptance:                           # 计划级验收；全部满足才能置 done
    - 受保护端点拒绝 cookie，仅接受 Bearer JWT
---

# {计划标题}

## 背景
{1-3 段：为什么做、现状、关键约束。}

## 任务依赖图
{任务 ≥4 或依赖非平凡时画 mermaid flowchart；节点用 Dotted ID。简单线性可省略。}

## 检查点
{每 2-4 个叶子一个检查点；executor 到达时暂停、跑验证。}
### Checkpoint A: 1.* 完成
- [ ] cookie 与 jwt 两条路径同时可走通

## 预计触碰文件
{各 leaf `files` 的并集。每条注明「修改/新建」+ 原因。}
- 修改 src/auth/SessionProvider.ts — 抽象出接口
- 新建 src/auth/JwtSession.ts — JWT 会话实现

## 风险与缓解
| 风险 | 影响 | 缓解 |
|---|---|---|

## 复盘笔记
{执行结束或受阻时填。replan、坑、对计划的偏离及原因。}
```

### leaf 任务文件 `<NN>-<kebab>.md`

```md
---
task:
  id: "1.1"                            # Dotted ID；必须与路径序号一致
  title: 抽象 SessionProvider 接口
  status: done                         # todo|in_progress|done|blocked（显式，executor 写）
  mode: react                          # 可选；缺省继承 default_mode
  depends: []                          # Dotted ID 列表（叶或组）；组依赖 = 其下叶子全 done
  acceptance:                          # 任务级验收——具体、可测
    - 存在 SessionProvider 抽象，CookieSession 通过它工作
  files:                               # 预计触碰面；executor 用于冲突检测
    - src/auth/SessionProvider.ts
    - src/auth/CookieSession.ts
  verification: pnpm test src/auth     # 可执行命令或可观察检查
---

# 1.1 · 抽象 SessionProvider 接口

{可选：任务说明、执行中产生的 notes。}
```

> group 节点**不**拥有这些字段——group 不可执行，无 `acceptance`/`verification`/`files`/`mode`。

## 状态词表

**计划级 `plan.status`**（存于 `plan.md`）：

| 值 | 含义 |
|---|---|
| `draft` | planner 仍在编写，未交付执行 |
| `ready` | 已完成、已自检、待执行（人审后置 `in_progress`） |
| `in_progress` | executor 正在跑 |
| `done` | 全叶子 done 且计划级 acceptance 满足 |
| `blocked` | 受阻且 executor 无法自解；需人介入或 replan |
| `abandoned` | 放弃；保留供复盘 |

**叶子 `task.status`**（存于各 leaf 文件，显式、executor 写）：`todo` | `in_progress` | `done` | `blocked`。

**group 状态**（**派生**、只读、不存储为真源；按优先级 roll-up）：

| 条件（自上而下首匹配） | 派生状态 |
|---|---|
| 任一子节点（递归）`blocked` | `blocked` |
| 所有叶子 `done` | `done` |
| 任一子节点（递归）`in_progress` | `in_progress` |
| 否则（全部 `todo`） | `todo` |

> **状态真源**：`plan.status` 在 `plan.md`；leaf `status` 在各 task 文件 frontmatter；group 状态由子节点实时计算（roll-up），**不存储**——executor 改 leaf 状态后，向上刷新各祖先 group `INDEX.md` 的派生状态行与进度，并刷新顶层 INDEX 该计划的进度列。tracker 据真源汇总并对账。

## 模式词表

`default_mode`（`plan.md`）与 leaf `mode` 取值（语义不变，选型见 `plan-create/references/mode-selection.md`）：

| 值 | 含义 |
|---|---|
| `react` | 单 agent 串行：思考→行动→观察，逐步推进 |
| `subagent` | 派发子 agent 并行/隔离执行（DAG 调度） |
| `hybrid` | react 外壳 + subagent 内核（默认首选） |

> planner 在 `default_mode` 写通盘决策；leaf `mode` 仅在与默认显著不同时写。**group 无 mode**（不可执行）。

## 参考标签词表

`plan.references[].tag`（YAML 列表，可多选）：

| 值 | 含义 |
|---|---|
| `important` | 核心/必读，直接决定目标成败 |
| `refer` | 参考，提供模式/约定/历史决策 |
| `context` | 背景，只解释为什么做 |
| `blocker` | 阻塞项，含未决决策或外部依赖，定稿前需先解决 |

## reference type 词表

`plan.references[].type`（单选）：

| 值 | 含义 |
|---|---|
| `prd` | 产品需求文档 |
| `issue` | issue 跟踪条目 |
| `spec` | `docs/spec/` 下的功能规格 |
| `adr` | `docs/adr/` 下的架构决策记录 |
| `doc` | 其他文档 / 外部链接 |

## 规则

- **唯一真源**：`plan.status` 在 `plan.md`；leaf `status` 在 task 文件；group 状态派生不存储。executor 不在内存里另持一份。
- **结构稳定**：frontmatter 块名（`plan` / `task`）与字段名（`goal`/`references`/`constraints`/`acceptance`/`default_mode`/`replan_count`；`id`/`title`/`status`/`mode`/`depends`/`acceptance`/`files`/`verification`）固定，不得自创同义词。group 无 frontmatter。
- **Dotted ID 一致**：每个节点声明的 `id` 必须与路径序号一致；`depends` 中的 id 必须存在；依赖图**计划内封闭**（不跨计划）。
- **写前先读**：executor/tracker 改读计划前必须先 `read` 相关文件与目录 `INDEX.md`，避免覆盖并发改动。
- **叶子可执行**：只有 leaf 携带 `acceptance`/`verification`/`files`/`mode`；group 不可执行，不携带这些字段。
- **计划级验收**：所有叶子 done **不等于**计划 done——必须 `acceptance` 全部满足，executor 才能置 `plan.status: done`。
- **范围自洽**：`plan.md`「预计触碰文件」段 = 各 leaf `files` 的并集；planner 自检时核对。
- **终态归档**：`plan.status: done` 时，executor 把**整个计划目录**移入 `completed/`；非 `done`（含 `abandoned`、`blocked`）一律留 `active/`。
- **索引随动**：create 新建计划、execute 改状态或归档时，同步顶层 `docs/plan/INDEX.md`；execute 改 leaf 状态时，同步刷新祖先 group `INDEX.md` 的派生状态行与进度（roll-up）。
