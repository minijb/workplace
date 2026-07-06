# 执行模式选型（plan-create 参考）

本文件给 `plan-create` skill §4 提供模式决策依据。**为 `default_mode` 取值前先 `read` 本文件。**

> 单位说明：本文件中「leaf」指任务树里唯一可执行的叶子节点；group 不可执行、无 mode。

## 三种模式

| 模式 | 机制 | 优势 | 代价 |
|---|---|---|---|
| `react` | 单 agent 串行：思考→行动→观察，逐步推进 | 上下文连续、可中途调整、调试友好 | 慢、token 随步数线性涨 |
| `subagent` | 派发子 agent 并行/隔离执行（DAG 调度，无依赖 leaf 并行） | 快、上下文隔离防爆、可并行 | 协调开销、子 agent 间不共享发现 |
| `hybrid` | react 外壳 + subagent 内核：串行骨架按依赖推进，独立 leaf 成波并行 | 兼顾连续性与并行度 | 复杂度最高，需正确切分串行/并行 |

## 决策树

按顺序回答：

```
1. 目标是否运行时才明确、需交互探索？
   是 → react
   否 → 2

2. leaf 是否相互独立、可并行？
   是 → 3
   否 → 5

3. 总规模是否大（>50K token 估算 / 触碰 >10 文件）？
   是 → subagent
   否 → 4

4. 是否需要领域专长或隔离上下文？
   是 → subagent
   否 → react（开销最小）

5. 是否存在明显可并行的独立波次，同时有必须串行的骨架？
   是 → hybrid（多数真实计划落这里）
   否 → 6

6. 串行 leaf 间是否需要共享上下文/发现？
   是 → react
   否 → subagent（按依赖分波）
```

## 各模式适用场景速查

### react 适合

- 调试、排障：每步依赖上一步观察。
- 重构跨文件符号：`lsp rename` 类，需连续上下文。
- 目标运行时才明确（探索性数据分析、动态文档对话）。
- leaf ≤3 个、强耦合、总规模小。
- 需要在过程中频繁向用户确认。

### subagent 适合

- leaf 相互独立（不同模块、不同子系统）。
- 总规模大——单 agent 上下文装不下或会爆。
- 需要领域专长（每个子 agent 专注一个领域）。
- 可重复的批处理（多个同构转换）。
- leaf 图是宽浅的 DAG（多个无依赖分支）。

### hybrid 适合（默认首选）

- 多数真实计划：有地基（串行）+ 功能切片（可并行）。
- 前几个 leaf 建抽象/契约（react），后续切片可分波并行（subagent）。
- 既想保留上下文连续性，又想压墙钟时间。

> **拿不准就选 `hybrid`。** 它是 react 与 subagent 的超集——executor 在 hybrid 下按 leaf 实际依赖与 mode 字段决定每段怎么跑。

## leaf 级 mode 覆盖

`default_mode` 是通盘默认（写在 `plan.md`）。单个 leaf 可在其 `task:` frontmatter 的 `mode` 字段覆盖，**仅在与默认显著不同时才写**（group 无 mode，不可执行）：

```md
# 文件 03-debug-cookie-race.md
---
task:
  id: "1.3"
  title: 调试 cookie 失效竞态
  mode: react           # 默认 hybrid，但调试 leaf 标 react
  depends: ["1.2"]
  ...
---

# 文件 01-audit-endpoints.md
---
task:
  id: "2.1"
  title: 给 8 个独立端点各加审计日志
  mode: subagent        # 8 个同构转换，天生可并行
  depends: ["1"]        # 依赖整个 group 1（其下叶子全 done）
  ...
---
```

判定"显著不同"：如果该 leaf 用默认模式跑会明显低效或出错，就标。否则省略，继承默认。

## 反模式

- **处处覆盖**：每个 leaf 都写 mode——说明 default_mode 选错了，回去改默认。
- **全 subagent 但 leaf 强耦合**：子 agent 互相等结果，并行变伪并行，还付出隔离开销。
- **全 react 但 leaf 相互独立**：放弃并行加速，墙钟时间翻倍。
- **调试 leaf 标 subagent**：调试需要连续上下文，subagent 隔离上下文正好毁掉它。
