---
name: grilling-with-context
description: 在盘问用户以压力测试一份计划或设计的同时，主动建立并打磨项目的领域模型，并把结晶的术语、关系与决策接入 docs 系统。当用户想在动工前用盘问（'grill' / 盘问）的方式厘清设计、统一领域术语、或沉淀难以回退的架构决策时使用。按 docs 系统约定把术语写进 CONTEXT.md、难逆决策写进 docs/adr/，必要时分流到 docs/spec 与 docs/reference，并同步各级 INDEX.md 与 CONTEXT-MAP.md。与 grilling-me 的区别：本 skill 边盘问边落盘到 docs 系统；grilling-me 只盘问不落盘。
---

# 带上下文的盘问（Grilling with Context）

把「盘问」「领域建模」与 **docs 系统**三者合在一起：一边就一份计划或设计对用户逐题盘问、走遍设计树的每个分支；一边把盘问中**结晶**的术语、关系与决策即时沉淀到 docs 系统的正确位置（`CONTEXT.md` 术语表、`docs/adr/` 决策，必要时 `docs/spec/` 与 `docs/reference/`）。**目标是在动工前与用户达成共识，同时让领域模型与文档比会话开始时更清晰、更一致。**

> **与 grilling-me 的关系**：`grilling-me` 是纯盘问、不落盘；本 skill 在盘问同时主动维护领域模型并写入 docs 系统——术语冲突就指出、模糊就收窄、决策结晶就落 ADR、未决就进 Open Questions。用户只想压力测试设计、不关心落盘时，用 `grilling-me`。

> **写 docs 不等于「执行计划」**：把已结晶的领域知识写入 docs 系统是本 skill 的本职，不受「未达成共识前不动工」约束。受约束的是开始实现设计本身。

## 0. 前置：接入 docs 系统并加载上下文

盘问前先（只读地）确认 docs 系统状态、建立现状心智模型：

1. **检查 docs 工作区**：`glob` 确认 `docs/` 及其 `INDEX.md`、各子目录 `INDEX.md` 是否就位（由 `docs-workspace` 搭建）。**未就位** → 告知用户先跑 `docs-workspace`；本 skill 仍可懒创建根级 `CONTEXT.md`，但不负责补全套脚手架。
2. **先索引后正文（始终遵守）**：进入 `docs/` 下任何目录（`spec` / `reference` / `adr`）都**先读该目录 `INDEX.md`**，再按需加载具体文件——禁止盲猜文件名。
3. **定位并读 CONTEXT.md**：根级有 `CONTEXT-MAP.md` → 多上下文，按 map 找到本次讨论所属上下文的 `CONTEXT.md`，并读根级共用 `CONTEXT.md`；无 → 用根级 `CONTEXT.md`。不存在 → 记下「尚无术语表」，待首个术语结晶时按 `skills/lib/context-format.md` 创建。
4. **读相关 ADR**：经 `docs/adr/INDEX.md` 找到与本次设计相关的 ADR 并读，避免重复决策或与既有决策冲突。
5. **扫代码**：`glob` / `grep` 本次设计涉及的源码区，确认现有命名与结构——盘问中要用代码印证用户陈述（§2）。

**格式以 docs 系统契约为准——写入前先 `read`：术语 `skills/lib/context-format.md`、ADR `skills/lib/adr-format.md`、索引 `skills/lib/index-format.md`。禁止凭记忆写格式。**

## 1. 盘问节奏

- **一次一题**：每次只问一个问题，并给出你**推荐的答案**，等用户反馈再继续。一次抛多题会让人无所适从。
- **遍历设计树**：沿设计的每个分支逐题推进，逐个理清决策间的依赖——先问被依赖最多的底层概念。
- **能查代码就别问**：一个问题若能通过探查代码库回答，就去探查，不要拿去问用户。
- **未达成共识不动工**：在用户确认共识前，不要开始实现这份设计。沉淀术语/决策到 docs 系统（§3）除外。

## 2. 盘问中主动打磨领域模型

盘问不是只问，每一题都要用下列动作打磨模型：

- **对撞术语表**：用户用的某个词与 `CONTEXT.md` 既有定义冲突 → 当场指出。「你的术语表把 'cancellation' 定义为 X，但你这里像是 Y——到底是哪个？」
- **收窄模糊用语**：用户用了模糊或过载的词 → 提出精确的规范术语。「你说 'account'——指 Customer 还是 User？这俩是不同的东西。」
- **拿具体场景施压**：讨论领域关系时，构造探测边界的具体场景（尤其边缘情况），逼用户把概念边界说精确。
- **用代码印证**：用户陈述某事如何工作时，去查代码是否一致；发现矛盾就揭出。「你的代码取消的是整个 Order，但你刚说可以部分取消——哪个对？」

## 3. 即时沉淀（接入 docs 系统）

结晶的知识**按类型路由到 docs 系统的正确位置**，当场写、不积压：

| 结晶的知识 | 去向 | 格式契约 |
|---|---|---|
| 术语定义 / 别名 / 反义词 | `CONTEXT.md` → `Language` | `context-format.md` |
| 术语间关系骨架 | `CONTEXT.md` → `Relationships` | `context-format.md` |
| **悬而未决的术语** | `CONTEXT.md` → `Open Questions` | `context-format.md` |
| 难回退 + 无背景会意外 + 真实权衡的决策 | `docs/adr/NNNN-slug.md` | `adr-format.md` |
| 功能规格 / 接口约定 / 验收标准（非术语） | `docs/spec/` | `index-format.md` |
| 外部 API / 规范 / 调研引用 | `docs/reference/` | `index-format.md` |

要点：

- **术语结晶即写**：一个术语达成一致，当场更新对应 `CONTEXT.md`。多上下文时，跨上下文通用术语归**根级**、模块专属归**模块** `CONTEXT.md`，不重复（必要时 `See also` 互链）。`CONTEXT.md` 只放术语，绝不塞实现/规格/草稿。
- **未决术语入 Open Questions**：盘问中一时定不下来的术语写进 `CONTEXT.md` 的 `Open Questions`——这是 grilling 的天然产物，写下来才不会被默默忽略；后续会话或 `plan-create` 可据其追问。
- **ADR 克制**：仅当三条**同时**成立才提议 ADR（难回退 / 无背景会意外 / 真实权衡，详见 `adr-format.md`「何时创建」）。编号扫 `docs/adr/` 取现有最大 +1。三条缺一即跳过。提议时给建议编号与一句话摘要，落盘与否由用户拍板。
- **同步 INDEX（写 `docs/` 文件时必做）**：在 `docs/` 下新增/删除任何文件，立即按 `index-format.md` 更新**同级** `INDEX.md` 一行说明——不积压。`CONTEXT.md` 在根或模块目录、不属 `docs/`，无需进 INDEX。
- **同步 CONTEXT-MAP（多上下文时）**：若盘问中**浮现一个新上下文**并新建了它的 `CONTEXT.md`，按 `context-format.md` 把它登记进根级 `CONTEXT-MAP.md` 的 `Contexts`，必要时补 `Relationships`。

## 4. 收敛

- 每解决一个分支，简述结论以及它如何（或无需）改动领域模型与 docs。
- 全部分支走完、与用户确认共识后，给出本次会话**对 docs 系统变更的摘要**：新增/修订了哪些术语与关系、哪些未决术语进了 Open Questions、新建了哪些 ADR / spec / reference、更新了哪些 INDEX / CONTEXT-MAP。
- 共识达成前不实现设计；共识达成后把「下一步」交还用户（实现归 `plan-execute`，规划归 `plan-create`，都不是本 skill）。

## 完成标准

- 设计树的每个分支都被逐题盘问到，或有用户明确的「这条先跳过」。
- 结晶的知识已按 §3 路由表落到 docs 系统的正确位置，格式符合对应 `skills/lib/*-format.md`。
- 在 `docs/` 下新增/删除的文件均已同步同级 `INDEX.md`；多上下文新建的 `CONTEXT.md` 已登记进 `CONTEXT-MAP.md`。
- 满足三条件的难逆决策已提议 ADR（落盘与否由用户定）；不满足三条件的未被滥建。
- 与用户就设计达成共识，或明确标注仍未解决的核心冲突（并已写入对应 `Open Questions`）。
- 已给出本次会话对 docs 系统变更的摘要。

## 不做什么

- 不实现设计、不写业务代码——动工归 `plan-execute`；规划归 `plan-create`。
- 不搭建全套 `docs/` 脚手架（各目录与 INDEX 的初始化、`.gitignore` 配置）——归 `docs-workspace`。本 skill 只为**自己写入的文件**维护同级 `INDEX.md` 一行，不替其他目录补建 INDEX。
- 不把 `CONTEXT.md` 当规格或草稿——它只是术语表；规格归 `docs/spec/`，决策归 `docs/adr/`。
- 不滥建 ADR——三条标准缺一即跳过。
- 未与用户达成共识前，不开始执行设计。
