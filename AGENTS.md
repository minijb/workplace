# AGENT.md

本工作区是**计划系统的 skills + docs 知识工作区**（非代码项目）：`.omp/skills/` 下 7 个 skill 配 `lib/` 四份共享格式契约，`docs/` 是其落地承载。进入工作区先读本文件。

## 目录地图

| 路径 | 是什么 |
|---|---|
| `.omp/skills/<name>/SKILL.md` | 各 skill 的入口与流程（精简） |
| `.omp/skills/<name>/references/`、`scripts/` | 下沉的长内容、模板、脚本（按需加载） |
| `.omp/skills/lib/*-format.md` | **共享格式契约（真源）**：`plan` / `context` / `adr` / `index` |
| `.omp/rules/` | 工作区规则（当前：`skill-progressive-disclosure`） |
| `docs/` | 文档工作区：`spec` / `generated` / `reference` / `adr` / `plan`，每目录有 `INDEX.md` |
| `docs/plan/{active,completed}/` | 计划树：`active/` 进行中、`completed/` 已归档，`plan/INDEX.md` 是注册表 |
| `CONTEXT.md` | 计划系统术语表（根级、单上下文） |
| `skills-质量评估综合报告.md` 等 | 评估与调研报告（参考，非运行时） |

## 按意图路由

| 我想做 | 用哪个 skill |
|---|---|
| 搭建/规整 docs 工作区脚手架 | `docs-workspace` |
| 只读查 docs 结构/术语/格式契约 | `use-docs`（全程只读，写入请走下表） |
| 动工前盘问厘清设计，**不落盘** | `grilling-me` |
| 盘问并沉淀术语 / ADR 到 docs | `grilling-with-context` |
| 把目标拆成可执行计划树 | `plan-create` |
| 推进/执行计划 | `plan-execute` |
| 查计划进度 / 阻塞 / drift | `plan-track`（只读） |

## 工作区纪律

**写 skill**
- **渐进式披露**：`SKILL.md` 只放入口与流程；模板、长示例、脚本下沉 `references/` / `scripts/`，按需 `skill://<name>/<path>` 加载。
- 每条主路径配平**边缘/失败路径**的明文处置；每个 skill 自声明定位与**兄弟 skill 边界**。

**跨文件契约**
- 引用基点统一：用相对 skills 根的全路径（如 `skills/lib/plan-format.md`），或在该 skill §0 显式声明 `references/` 基点。
- **单一真源**：规则委托给 `lib/*-format.md`，正文不复述整表；但易误读术语处补一行交叉引用消歧。
- 凡要求产出的"空骨架 / 逐字 pattern"，在 lib 或 skill 内联一份删净示例的版本。

**docs 工作区**
- 进入任一目录先读其 `INDEX.md`。
- `lib/*-format.md` 是真源，`CONTEXT.md` / 各 `INDEX.md` 是看板——状态以对应真源（`plan.md` frontmatter / leaf frontmatter）为准。
- `docs/generated/` 入 `.gitignore` 但仍维护 `INDEX.md`（供当次会话定位产物）。
