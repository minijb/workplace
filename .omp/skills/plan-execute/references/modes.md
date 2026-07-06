# 执行模式协议（plan-execute 参考）

本文件给 `plan-execute` skill §1/§3 提供三种模式的执行协议。**切模式前先 `read` 对应章节。**

三种模式共享同一个**单 leaf 执行循环**（plan-execute §3）：改状态→实现→验证→验收→改状态→刷新 roll-up。区别在** leaf 间如何调度**。

> 本文件假设已读 `skills/lib/plan-format.md`：只有 **leaf** 可执行；**group** 不可执行；leaf `depends` 用 Dotted ID，依赖一个 group = 其下叶子全 done。

---

## react：单线程串行

每个 agent 步骤依赖上一步的观察。最简单、上下文最连续。

### 协议

```
while 存在 status==todo 且 depends 全 done 的 leaf:
    leaf = 拓扑序最前的就绪 leaf
    执行 leaf（单 leaf 循环：in_progress → 实现 → verify → acceptance → done → 刷新 roll-up）
    if leaf 是 checkpoint 边界: 跑检查点；失败则停
若全部 leaf done: 校验 plan.acceptance → plan.status=done → 归档目录
```

### 何时自然落到 react

- 用户显式指定 `react`。
- 计划 `default_mode: react`。
- `hybrid` 模式下进入串行骨架段（见下）。

### 要点

- 一次只做一个 leaf，做完才取下一个。
- 上下文连续是 react 的核心价值——不要中途切换到子 agent 做相关 leaf，会丢失连续性。
- 调试类 leaf（`mode: react` 覆盖）即便在 hybrid/subagent 计划中也按本协议跑。

---

## subagent：DAG 调度并行

按依赖把 leaf 分成**波次**：一个波次是当前所有 `todo` 且依赖已 `done` 的 leaf。波次内 leaf **相互无依赖**，可并行派发子 agent。波次间 barrier——上一波全部 `done` 才进入下一波。

### 协议

```
while 存在 status==todo 的 leaf:
    wave = { leaf | leaf.status==todo 且 leaf.depends 全 done }   # 本波就绪集
    if wave 为空且有 todo: 依赖断裂 → replan/blocked（见 plan-execute §5）
    if wave 中 leaf 对同一文件有写冲突:
        把冲突 leaf 拆到不同波次（按 depends 外的 files 冲突图排序）
    用 task 工具派发 wave 中每个 leaf 为一个子 agent，并行
    barrier：等本波全部子 agent 返回
    每个子 agent 内部跑单 leaf 循环（in_progress → 实现 → verify → acceptance → done）
    主 agent 收到结果后刷新各 leaf 状态、向上 roll-up 刷新祖先 group INDEX + 顶层进度
    若某子 agent 失败：见下「失败隔离」
跑检查点 / 校验 plan.acceptance
```

### 失败隔离

- 一个子 agent 失败**不阻塞**同波独立分支——其它子 agent 继续跑完。
- 失败 leaf：若可在原 acceptance 内修，由主 agent 接手按 react 修（≤2 次）；否则标 `blocked` 或触发局部 replan。
- 失败的下游 leaf（depends 失败 leaf）自动延后到失败 leaf 解决。

### 冲突检测

派发波次前，扫描本波所有 leaf 的 `files` 列表：

- 两个 leaf 触碰同一文件 → 视为写冲突，强制拆到不同波次（保留拓扑序）。
- 三 leaf 互触同一文件 → 串成三波，每波一个。
- 没有冲突 → 全部并行。

这是 subagent 模式的正确性兜底——并行写同一文件会撕裂。

### 子 agent 的指派

每个子 agent 的 `assignment` 至少包含：

- leaf 的标题、`acceptance`、`files`、`verification`（从 leaf 文件复制，不依赖子 agent 读计划树）。
- "完成后通过 task 返回的结果里声明：done/blocked + 跑过的 verification 输出摘要"。
- 约束：触碰面限定在 `files`，不做 acceptance 外的事。

主 agent 收到子 agent 结果后，把对应 leaf 的 `status` 写回 leaf 文件、刷新 `plan.md` 的 `updated`，并向上 roll-up 刷新祖先 group `INDEX.md` 的派生状态行 + 顶层 INDEX 该计划进度列。

---

## hybrid：react 骨架 + 波次并行

串行推进依赖链，遇到独立可并行的 leaf 群就切 subagent 跑一波，然后回到串行。**多数真实计划的默认。**

### 协议

```
while 存在 status==todo 的 leaf:
    wave = { leaf | leaf.status==todo 且 leaf.depends 全 done }
    if wave 大小 == 1:
        按 react 协议做这一个 leaf         # 串行骨架
    else:
        检查 files 冲突：
          - 无冲突 → 整波按 subagent 协议并行
          - 有冲突 → 冲突 leaf 按 react 串行，其余按 subagent 并行
    跑检查点 / replan 判定
```

### 判定"何时切并行"

满足任一即切 subagent 跑波次：

- wave 大小 ≥ 2 且 leaf 相互独立（不同模块/不同文件）。
- wave 中存在标了 `mode: subagent` 的 leaf（即便其它默认 react，也整波并行）。

否则按 react 串行处理 wave（即便有多个就绪 leaf）。

### 与 leaf 级 mode 的交互

- leaf 级 `mode: react` 在 hybrid 下表示"这个 leaf 串行做"——但若它恰好与其它独立 leaf 同波，仍可并行（mode 是建议，不是硬约束）。**例外**：调试类 leaf（`mode: react` + acceptance 是排障）应**强制串行**，避免丢失上下文。
- leaf 级 `mode: subagent` 在 hybrid 下表示"这个 leaf 适合并行"——若它在单 leaf 波次里，就单做；在多 leaf 波次里就并入并行。

### 反模式

- **整计划强行套一种模式**——hybrid 的价值是按 leaf 特性切换；不切换等于退化成 react 或 subagent。
- **波次粒度太细**（每波一 leaf）——并行度为 1，付出调度开销却没拿到加速；不如直接 react。
- **波次粒度太粗**（把依赖链当成一波）——子 agent 互相等结果，伪并行。

---

## 模式间共享的不变量

不论哪种模式，这些**必须**成立：

- 状态真源是文件：`plan.status` 在 `plan.md`；leaf `status` 在各 leaf 文件；group 状态派生不存储。状态改动**立刻** `write` 落盘，不在内存持副本。
- 单 leaf 循环固定：in_progress → 实现 → verify → acceptance → done（acceptance 不满足不能 done）→ 刷新 roll-up（祖先 group INDEX 派生状态行 + 顶层进度）。
- checkpoint 是硬暂停点：不跑过验证不跨。
- 写文件用 `write` 全文件，不用 `edit` 局部改。
- 只有 leaf 被调度执行；group 永不执行。
