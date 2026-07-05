# 执行模式协议（plan-execute 参考）

本文件给 `plan-execute` skill §1/§3 提供三种模式的执行协议。**切模式前先 `read` 对应章节。**

三种模式共享同一个**单任务执行循环**（plan-execute §3）：改状态→实现→验证→验收→改状态。区别在**任务间如何调度**。

---

## react：单线程串行

每个 agent 步骤依赖上一步的观察。最简单、上下文最连续。

### 协议

```
while 存在 status==todo 且 depends 全 done 的任务:
    t = 拓扑序最前的就绪任务
    执行 t（单任务循环：in_progress → 实现 → verify → acceptance → done）
    if t 是 checkpoint 边界: 跑检查点；失败则停
若全部 done: 校验 plan.acceptance → plan.status=done
```

### 何时自然落到 react

- 用户显式指定 `react`。
- 计划 `default_mode: react`。
- `hybrid` 模式下进入串行骨架段（见下）。

### 要点

- 一次只做一个任务，做完才取下一个。
- 上下文连续是 react 的核心价值——不要中途切换到子 agent 做相关任务，会丢失连续性。
- 调试类任务（`mode: react` 覆盖）即便在 hybrid/subagent 计划中也按本协议跑。

---

## subagent：DAG 调度并行

按依赖把任务分成**波次**：一个波次是当前所有 `todo` 且依赖已 `done` 的任务。波次内任务**相互无依赖**，可并行派发子 agent。波次间 barrier——上一波全部 `done` 才进入下一波。

### 协议

```
while 存在 status==todo:
    wave = { t | t.status==todo 且 t.depends 全 done }   # 本波就绪集
    if wave 为空且有 todo: 依赖断裂 → replan/blocked（见 plan-execute §5）
    if wave 中任务对同一文件有写冲突:
        把冲突任务拆到不同波次（按 depends 外的 files 冲突图排序）
    用 task 工具派发 wave 中每个任务为一个子 agent，并行
    barrier：等本波全部子 agent 返回
    每个子 agent 内部跑单任务循环（in_progress → 实现 → verify → acceptance → done）
    若某子 agent 失败：见下「失败隔离」
跑检查点 / 校验 plan.acceptance
```

### 失败隔离

- 一个子 agent 失败**不阻塞**同波独立分支——其它子 agent 继续跑完。
- 失败任务：若可在原 acceptance 内修，由主 agent 接手按 react 修（≤2 次）；否则标 `blocked` 或触发局部 replan。
- 失败的下游任务（depends 失败任务）自动延后到失败任务解决。

### 冲突检测

派发波次前，扫描本波所有任务的 `files` 列表：

- 两个任务触碰同一文件 → 视为写冲突，强制拆到不同波次（保留拓扑序）。
- 三任务互触同一文件 → 串成三波，每波一个。
- 没有冲突 → 全部并行。

这是 subagent 模式的正确性兜底——并行写同一文件会撕裂。

### 子 agent 的指派

每个子 agent 的 `assignment` 至少包含：

- 任务标题、acceptance、files、verification（从计划复制，不依赖子 agent 读计划）。
- "完成后通过 task 返回的结果里声明：done/blocked + 跑过的 verification 输出摘要"。
- 约束：触碰面限定在 `files`，不做 acceptance 外的事。

主 agent 收到子 agent 结果后，把对应任务的 `status` 写回计划文件并刷新 `plan.updated`。

---

## hybrid：react 骨架 + 波次并行

串行推进依赖链，遇到独立可并行的任务群就切 subagent 跑一波，然后回到串行。**多数真实计划的默认。**

### 协议

```
while 存在 status==todo:
    wave = { t | t.status==todo 且 t.depends 全 done }
    if wave 大小 == 1:
        按 react 协议做这一个任务         # 串行骨架
    else:
        检查 files 冲突：
          - 无冲突 → 整波按 subagent 协议并行
          - 有冲突 → 冲突任务按 react 串行，其余按 subagent 并行
    跑检查点 / replan 判定
```

### 判定"何时切并行"

满足任一即切 subagent 跑波次：

- wave 大小 ≥ 2 且任务相互独立（不同模块/不同文件）。
- wave 中存在标了 `mode: subagent` 的任务（即便其它任务默认 react，也整波并行）。

否则按 react 串行处理 wave（即便有多个就绪任务）。

### 与任务级 mode 的交互

- 任务级 `mode: react` 在 hybrid 下表示"这个任务串行做"——但若它恰好与其它独立任务同波，仍可并行（mode 是建议，不是硬约束）。**例外**：调试类任务（`mode: react` + acceptance 是排障）应**强制串行**，避免丢失上下文。
- 任务级 `mode: subagent` 在 hybrid 下表示"这个任务适合并行"——若它在单任务波次里，就单做；在多任务波次里就并入并行。

### 反模式

- **整计划强行套一种模式**——hybrid 的价值是按任务特性切换；不切换等于退化成 react 或 subagent。
- **波次粒度太细**（每波一任务）——并行度为 1，付出调度开销却没拿到加速；不如直接 react。
- **波次粒度太粗**（把依赖链当成一波）——子 agent 互相等结果，伪并行。

---

## 模式间共享的不变量

不论哪种模式，这些**必须**成立：

- 计划文件是唯一真源：状态改动**立刻** `write` 落盘，不在内存持副本。
- 单任务循环固定：in_progress → 实现 → verify → acceptance → done（acceptance 不满足不能 done）。
- checkpoint 是硬暂停点：不跑过验证不跨。
- 写计划用 `write` 全文件，不用 `edit` 局部改。
