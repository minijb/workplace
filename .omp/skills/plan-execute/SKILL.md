---
name: plan-execute
description: 规划系统的 Executor 阶段。读取一份 docs/plan/active/ 下的计划目录（任务树），遍历树找到就绪的叶子任务，按 default_mode（react / subagent / hybrid）推进、跑 verification、更新叶子状态并向上刷新 group 派生状态（roll-up）。用户可显式指定执行模式覆盖默认值。出错时按 replan 规程处理。不创建计划——创建归 plan-create，查进度归 plan-track。
---

# 计划系统 · 执行（Executor）

按一份既定计划把叶子任务跑完。本 skill 是计划系统的**写入**阶段：遍历任务树、推进叶子状态、跑验证、刷新 roll-up、必要时 replan。**只执行叶子（leaf），不自创新节点；group 不可执行。**

> **三 skill 关系**：`plan-create`（规划）→ `plan-execute`（本 skill，执行）→ `plan-track`（查进度）。共享契约 `skills/lib/plan-format.md`——**执行前先 `read` 它**，确认 Dotted ID、状态/模式词表、roll-up 规则、两层 INDEX。
>
> **核心模型**：计划 = 任务树。只有 **leaf**（`.md` 文件）可执行；**group**（目录）不可执行，其状态由子节点 roll-up 派生（只读）。executor 永远在 leaf 上工作。

## 0. 前置：读契约、读计划

1. `read skills/lib/plan-format.md`——确认字段、Dotted ID 解析、状态/模式词表、roll-up 规则（每次执行都读，不靠记忆）。
2. 用户指定计划时 `read` 其 `plan.md`；未指定时先读顶层 `docs/plan/INDEX.md`，再（必要时）扫 `docs/plan/active/*/plan.md` 取 `status: ready`/`in_progress` 中最新的。
3. **遍历树建立心智模型**：从计划根 `INDEX.md` 起，沿 group 子目录递归读各 `INDEX.md`，枚举全部 leaf 及其 `status`/`depends`。改读前先读全相关文件，避免覆盖并发改动。

## 1. 确认执行模式

`plan.md` 的 `default_mode` 是默认。用户可在调用时显式覆盖：

- 用户指定 `react` / `subagent` / `hybrid` → 本次全程用指定模式（不改写 `default_mode`，仅本次覆盖）。
- 用户未指定 → 用计划 `default_mode`。

单个 leaf 的 `mode` 字段**始终生效**（覆盖本次会话默认）。**group 无 mode**。

**三种模式的执行协议见 `references/modes.md`——切模式前先 `read` 对应章节。** 速览：

| 模式 | 协议 |
|---|---|
| `react` | 单线程串行：取下个就绪 leaf→实现→跑 verification→更新状态→刷新 roll-up→下一个 |
| `subagent` | DAG 调度：按依赖分波，无依赖 leaf 派发子 agent 并行，波次间 barrier |
| `hybrid` | react 骨架 + 波次并行：串行推进依赖链，遇独立波次切 subagent |

## 2. 取下个就绪 leaf

一个 leaf "就绪"当且仅当：

- `status: todo`
- `depends` 中所有 Dotted ID 解析到的节点状态为"done"——解析到的若是 **leaf**，需 `status: done`；若是 **group**，需其派生状态为 `done`（即其下所有叶子 done）。

**Dotted ID 解析**：从计划根起，按 ID 段匹配对应序号的子节点（`1.2` → 根的第 1 个子节点 → 其第 2 个子节点），定位到 leaf 文件或 group 目录。

若多个 leaf 就绪：

- `react`：取拓扑序最前的。
- `subagent` / `hybrid`：**全部**就绪 leaf 组成一个波次并行派发（详见 `references/modes.md`）。

若无就绪 leaf 且有 `in_progress` → 继续该 leaf。若无就绪且无 `in_progress`、还有 `todo` → 前置链断了，进 §5 replan 或标 `blocked`。

## 3. 执行单 leaf（react / 单 leaf 视角）

不论整体模式，**单个 leaf** 的执行循环节奏：

1. **改状态**：`read` 该 leaf 文件，把 `status` 从 `todo` 改 `in_progress`；刷新 `plan.md` 的 `updated`；`write` 回该 leaf 文件（写全文件）。
2. **实现**：按 `acceptance` 做最小改动满足之。触碰 `files` 列出的路径；发现需触碰计划外文件，先在 leaf 正文 `notes` 备注。
3. **验证**：跑 `verification` 命令。失败 → 修；反复失败超 2 次 → 进 §5。
4. **验收**：逐条核对 `acceptance`——全部可观察满足才算完成。
5. **改状态 + 刷新 roll-up**：`status: done`；刷新 `plan.md` 的 `updated`；`write` 该 leaf 文件；然后**向上刷新 roll-up**——重算每个祖先 group `INDEX.md` 的派生状态行与进度（规则见 `plan-format.md`「状态词表」），并刷新顶层 `docs/plan/INDEX.md` 该计划行的进度列（done 叶子数 / 总叶子数）。
6. **检查点**：若该 leaf 属于某 checkpoint 边界，暂停跑检查点验证；失败则不继续，进 §5 或请求人审。

**写状态用 `write` 写全文件**，不用 `edit` 局部改——状态真源是文件，写全文件避免遗漏并发改动。roll-up 刷新只改 group `INDEX.md` 的派生状态行/进度，不改 group 的"真源"（group 状态本就不存储为真源，只是显示值）。

## 4. 检查点

到达 checkpoint 边界时（检查点定义在 `plan.md`「检查点」段）：

- 跑该 checkpoint 列出的全部验证。
- 全过 → 继续。
- 任一失败 → 不跨过 checkpoint。优先就地修；修不动进 §5；属于不可逆或人审门 → 暂停并向用户报告，等指示。

## 5. 出错与 Replan

leaf 失败、验证反复不过、发现计划缺陷（acceptance 不可达、依赖缺失、files 漏标关键文件）时，**不要硬冲**。**Replan 规程见 `references/replan.md`——出错时先 `read` 它。** 决策树速览：

```
leaf 失败
├─ 可在原 acceptance 内修 → 修，重试 ≤2 次
├─ acceptance 本身有缺陷/不可达 → 局部 replan：改该 leaf 的 acceptance/verification（不动树结构）
├─ 计划级缺陷（依赖断裂、目标不可达、需拆 leaf）→ 标 plan.status: blocked，向用户报告
└─ 触发收敛上限（全局 replan ≥3 次仍未收敛）→ 标 blocked
```

replanned 后必须刷新 `plan.md` 的 `updated` 并在「复盘笔记」段记一笔（改了哪个 leaf、改了什么、为什么）。

## 6. 计划级完成

全部叶子 `done` **不等于**计划完成。executor 必须再：

1. 逐条核对 `plan.md` 的计划级 `acceptance`——全部可观察满足。
2. 跑所有 checkpoint 验证。
3. 全过 → `plan.status: done`；刷新 `updated`。
4. **归档**：把**整个计划目录**从 `docs/plan/active/` 移到 `docs/plan/completed/`；把顶层 `docs/plan/INDEX.md` 该行从「进行中」段挪到「已完成」段（补完成日与一句话结果）。
5. 在 `plan.md`「复盘笔记」段简记：实际模式与计划的偏差、踩到的坑、对后续计划的建议。

任一不满足 → 不置 `done`；能修则修，不能修标 `blocked` 并报告缺什么。

## 7. 完成标准（本 skill 的退出条件）

- 要么 `plan.status: done`（计划级 acceptance 全满足）；
- 要么 `plan.status: blocked`（受阻且无法自解，已写明缺什么、试过什么）；
- 要么用户中断。
- 退出前所有改动已落盘：leaf 状态、`plan.md` 的 `updated`、各祖先 group `INDEX.md` 的派生状态行、顶层 INDEX 进度列已刷新；若置 `done`，整个计划目录已移入 `completed/` 且顶层 INDEX 已挪行；复盘笔记已记。

## 不做什么

- 不创建计划、不改任务树结构（加/删/改 group/leaf、改 Dotted ID 拓扑）——那是 `plan-create`。replan 仅在出错时局部改单个 leaf 的 `acceptance`/`verification`，不动树。
- 不查询进度报表——那是 `plan-track`。executor 改状态，不生成汇报。
- 不越界：只做 leaf `acceptance` 内的事；发现额外需求写进 leaf `notes`，不擅自扩。
- 不执行 group——group 不可执行，无 acceptance/verification/files。
- 不把非 `done` 状态的计划移入 `completed/`——`abandoned`/`blocked` 留 `active/`；归档仅限终态 `done`，且移动**整个计划目录**。
