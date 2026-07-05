# Plan 文件格式（计划系统共享契约）

`plan-create`、`plan-execute`、`plan-track` 三个 skill 共用本格式。计划文件是计划系统的**唯一持久状态**：planner 写入它、executor 读写它（推进状态）、tracker 只读它。三者都**必须先读本文件**再操作任何计划。

## 存放位置

```
docs/plan/<slug>-<YYYYMMDD>.md
```

- `docs/plan/` 由 `docs-workspace` skill 创建为空目录；本系统向其中写入计划文件。
- `<slug>`：短 kebab-case 标识，描述计划目标（如 `auth-jwt-migration`）。
- `<YYYYMMDD>`：创建日期，避免重名并便于排序。
- 例：`docs/plan/auth-jwt-migration-20260705.md`。
- **不创建 `docs/plan/INDEX.md`**——发现机制是扫 `docs/plan/*.md` 读 frontmatter（见 plan-track）。

## 文件结构

YAML frontmatter 承载**机器可读**的结构化字段；正文承载**人机可读**的背景、依赖图、任务、检查点。

```md
---
plan:
  id: auth-jwt-migration-20260705      # 与文件名（去 .md）一致，全局唯一
  title: 把会话认证从 cookie 迁移到 JWT
  goal: >-                              # 一句话目标：做什么、达成什么（不是怎么做）
    所有受保护端点改用 Bearer JWT；旧 cookie 路径在一个版本后下线
  status: in_progress                   # 见「状态词表」
  default_mode: hybrid                  # 见「模式词表」——由 planner 决定，可被单任务覆盖
  created: 2026-07-05
  updated: 2026-07-05                   # executor 每次推进任务状态时同步刷新
  constraints:                          # 计划级硬约束；executor 不得违反
    - 鉴权中断不超过 5 分钟
    - 旧 cookie 路径保留 1 个版本做灰度
  acceptance:                           # 计划级验收；全部满足才能置 done
    - 受保护端点拒绝 cookie，仅接受 Bearer JWT
    - 旧 cookie 路径返回 410 Gone
---

# {计划标题}

## 背景
{1-3 段：为什么做、现状、关键约束。写给人看，给六个月后的自己看。}

## 任务依赖图
{仅当任务数 ≥ 4 或依赖非平凡时画。用 mermaid flowchart 表达 T1→T2 关系。简单线性计划可省略。}

## 任务清单

### T1: 抽象 SessionProvider 接口
- status: done                         # 见「状态词表」；executor 推进时改这里
- mode: react                          # 可选；缺省继承 default_mode
- depends: []                          # 任务 id 列表；空数组表示无前置
- acceptance:                          # 任务级验收——具体、可测
  - 存在 SessionProvider 抽象，CookieSession 通过它工作
- files:                               # 预计触碰面；executor 用于冲突检测
  - src/auth/SessionProvider.ts
  - src/auth/CookieSession.ts
- verification: pnpm test src/auth     # 可执行命令或可观察检查
- notes: {可选，执行中产生的备注}

### T2: 实现 JwtSessionProvider
- status: todo
- mode: subagent
- depends: [T1]
- acceptance:
  - JwtSessionProvider 通过 SessionProvider 契约的全部测试
- files: [src/auth/JwtSession.ts]
- verification: pnpm test src/auth/jwt

## 检查点
{每 2-4 个任务一个检查点；executor 到达时暂停、跑验证、必要时请求人审。}

### Checkpoint A: T1-T2 完成
- [ ] cookie 与 jwt 两条路径同时可走通
- [ ] 切换开关存在且生效

## 风险与缓解
| 风险 | 影响 | 缓解 |
|---|---|---|

## 复盘笔记
{执行结束或受阻时填。记录 replan、踩到的坑、对计划的偏离及原因——供下次规划复用。}
```

## 状态词表

**计划级 `plan.status`**：

| 值 | 含义 |
|---|---|
| `draft` | planner 仍在编写，未交付执行 |
| `ready` | 已完成、已自检、待执行（人审后置 `in_progress`） |
| `in_progress` | executor 正在跑 |
| `done` | 全部任务 done 且计划级 acceptance 满足 |
| `blocked` | 受阻且 executor 无法自解；需人介入或 replan |
| `abandoned` | 放弃；保留文件供复盘 |

**任务级 `status`**：`todo` | `in_progress` | `done` | `blocked`。

> 任务状态是 executor 推进进度的**唯一来源**。每开始/完成一个任务，executor 直接改对应任务的 `status` 行，并刷新 `plan.updated`。tracker 据此汇总。

## 模式词表

`default_mode` 与任务级 `mode` 取值：

| 值 | 含义 | 何时用（详见 plan-create/references/mode-selection.md） |
|---|---|---|
| `react` | 单 agent 串行：思考→行动→观察，逐步推进 | 任务耦合紧、需上下文连续、调试类、目标运行时才明确 |
| `subagent` | 派发子 agent 并行/隔离执行（DAG 调度） | 任务相互独立、规模大（>50K token 估算）、需领域专长 |
| `hybrid` | react 外壳 + subagent 内核：串行骨架，独立波次并行 | 默认首选；耦合与独立并存的多数真实计划 |

> planner 在 `default_mode` 写入**通盘决策**；任务级 `mode` 仅在与默认显著不同时才写（如默认 hybrid，但某调试任务标 react）。

## 规则

- **唯一真源**：计划的全部状态——任务、依赖、进度、模式——只存在于本文件。executor 不在内存里另持一份。
- **结构稳定**：frontmatter 字段名、任务子键名（`status`/`mode`/`depends`/`acceptance`/`files`/`verification`）固定，不得自创同义词。
- **写前先读**：executor/tracker 改读计划前必须先 `read` 整个文件，避免覆盖并发改动。
- **正文可演化**：背景、风险、复盘段落自由格式；结构化部分（frontmatter + 任务字段）严格按本格式。
- **依赖闭环**：每个 `depends` 中的 id 必须存在；executor 不会调度前置未全 `done` 的任务。
- **计划级验收**：所有任务 done **不等于**计划 done——必须 `acceptance` 全部满足，executor 才能置 `plan.status: done`。
