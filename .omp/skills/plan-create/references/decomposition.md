# 任务分解策略（plan-create 参考）

本文件给 `plan-create` skill §3 提供分解方法。**分解任务前先 `read` 本文件。**

> 本文件假设你已读 `skills/lib/plan-format.md`：节点二元——**group**（目录，按功能分组、不可执行、状态派生）与 **leaf**（`.md` 文件，唯一可执行、状态显式），用 **Dotted ID** 标识。

## 核心原则：按功能切成 group，group 内落到 leaf

分解是两步：先按**功能**切成若干 **group**（每个 group 端到端覆盖一段可测功能），再把每个 group 落到原子 **leaf**。**group 是组织单位，leaf 是执行单位。**

**坏的（横向铺层）**——按技术层铺，最后才连：

```
group 1: 建全部数据库 schema
group 2: 建全部 API 端点
group 3: 建全部 UI 组件
```

问题：前几个 group 完成时没有任何可测功能；集成风险堆积到最后。

**好的（垂直切片）**——每个 group 端到端打通一条可测功能路径，group 内 leaf 是其原子步骤：

```
group 1: 用户能注册
  leaf 1.1: 用户表 schema + migration
  leaf 1.2: 注册 API
  leaf 1.3: 注册 UI
group 2: 用户能登录
  leaf 2.1: 登录 API
  leaf 2.2: 登录 UI
```

每个 group 交付**工作、可测**的功能；集成风险被分散到每个 group 内持续消化。

## MECE：兄弟节点相互独立、完全穷尽

- **相互独立**：同一 group 下的兄弟 leaf 不应做同一件事；同一 group 下的兄弟 group 不应重叠。重叠就合并或划清边界。
- **完全穷尽**：根 group 的全部直接子节点合起来必须能达成 `goal`。自检：完成全部 leaf 后，计划级 `acceptance` 是否必然满足？若否，缺节点——补上。

判定技巧：把兄弟节点标题列出来，逐对问"这俩是同一件事吗？"，再问"做完这些，父目标达成了吗？"。

## leaf 尺寸标准

尺寸标准只适用于 **leaf**（group 不可执行，不套此表）：

| 尺寸 | 触碰文件 | 范围 | 处置 |
|---|---|---|---|
| XS | 1 | 单函数或配置改 | 直接做 |
| S | 1-2 | 一个组件或端点 | 直接做 |
| M | 3-5 | 一个功能切片内的原子步 | 直接做 |
| L | 5-8 | 多组件 | **拆**：提升为 group + 子 leaf |
| XL | 8+ | — | **必须拆** |

executor 在单个 leaf 上表现最好的是 S-M。L 及以上的 leaf **必须继续拆**——把它从 leaf 提升为一个 **group**，下挂若干更小的 leaf。

**继续拆的信号**（命中任一就把该 leaf 升级为 group）：

- leaf 标题里出现"和"/"以及"——多半是两个 leaf。
- 触碰 ≥2 个相互独立的子系统（如 auth 和 billing）。
- acceptance 写不出 ≤3 条具体可测条件。
- 估算 executor 要跨多次专注会话才能完成。

## 何时不要再拆（停止递归）

过度分解同样有害——树太深则依赖图爆炸、协调开销压过实现。停止信号：

- leaf 已是 S-M 尺寸。
- acceptance 清晰可测。
- 与兄弟边界明确。
- 进一步拆只会产生"建文件""导出符号"这种本身无价值的碎片。

满足全部即可停止。**group 层级一般不超过 3 层**——更深通常意味着把 leaf 拆得太碎。

## leaf 必备的字段

```md
---
task:
  id: "1.2"
  title: 实现 JwtSessionProvider
  status: todo
  mode: subagent              # 可选，缺省继承 default_mode
  depends: ["1.1"]            # Dotted ID 列表（叶或组）
  acceptance:                 # 具体可测
    - JwtSessionProvider 通过 SessionProvider 契约的全部测试
    - token 过期后端点返回 401
  files: [src/auth/JwtSession.ts]
  verification: pnpm test src/auth/jwt
---
```

- **id**：Dotted ID，必须与路径序号一致（`01-.../02-...md` → `1.2`）。
- **acceptance**：回答"做对了吗"。每条要能跑命令或能点开验证。
- **verification**：可执行命令或可观察检查。
- **depends**：Dotted ID 列表。executor 不会在前置未全 done 时调度本 leaf。依赖一个 group（如 `depends: ["1"]`）= 该 group 下所有叶子 done。
- **files**：预计触碰面。executor 用它做冲突检测（subagent 模式下尤其重要）。

## 依赖排序

实现序 = 依赖图的拓扑序。规则：

1. **地基先行**：被依赖最多的底层抽象（schema、契约接口）先做。
2. **每个 leaf 后系统仍可工作**：不要产生"做完 1.2 系统就不能编译"的中间态——要么自包含，要么拆小。
3. **高风险前置**：不确定的技术选型、外部依赖、新接口——尽早做，失败早暴露。
4. **检查点每 2-4 leaf**：列入 `plan.md`「检查点」段。检查点是 executor 的暂停点。

## 反模式

| 反模式 | 表现 | 修正 |
|---|---|---|
| 水平铺层 | group 按"全部 schema / 全部 API"分 | 改垂直切片，每个 group 端到端 |
| 标题含"和" | 一个 leaf "实现登录和注册" | 升级为 group，拆成两个 leaf |
| 无 acceptance | leaf 只说"实现该功能" | 写出可测条件 |
| 无 verification | 只说"测试通过" | 给出具体命令 |
| 悬空依赖 | depends 引用不存在的 Dotted ID | 修引用或补节点 |
| XL leaf | 单 leaf 触碰 8+ 文件 | 升级为 group + 子 leaf |
| 隐藏集成 | 最后一个 group 叫"连接一切" | 集成风险分散到每个 group |
| group 过深 | 超过 3 层嵌套 | leaf 拆得太碎，合并 |
