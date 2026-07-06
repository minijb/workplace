# 0001: 计划从单文件改为多文件任务树

**背景**：原 `skills/lib/plan-format.md` 把一个计划存为单个 `.md`，任务以 `T1/T2` 段落内联。无法按功能把一个大任务拆成多个互相关联的文件，也无法表达「大任务→小任务→以此类推」的层级与逐节点状态、逐节点完成进度。

**决定**：计划改为**镜像任务层级的文件/目录树**。根 group 目录下放 `plan.md`（计划级 frontmatter：goal/references/constraints/acceptance/default_mode/status）与本地 `INDEX.md`；每个 group 子目录自相似地有自己的 `INDEX.md`（直系子节点 + 角色 + 状态 + 进度）；每个 leaf task 是一个 `.md` 文件。节点角色二元：**group**（按功能分组 + 状态聚合，**不可执行**，状态**派生**）与 **leaf**（唯一可执行，保留旧 `T` 级语义，状态显式）。**Dotted ID**（`1.2.3`）替代扁平 `T` 编号，计划内唯一；依赖图**计划内封闭**（不跨计划）。**只有根计划**在全叶子 `done` 且计划级 `acceptance` 满足时，把整个计划目录归档到 `completed/`。

## Status

accepted

## Considered Options（均被否决）

- **平铺文件 + parent 字段**（盘问 Q1）：递归不在文件夹结构上可见，「分功能」分组不直观。
- **固定层 Epic/Story/Task**（Q2）：层数固定、与任意深度递归冲突、带语义包袱。
- **group 状态显式可写**（Q4）：漂移风险，「全部才完成」靠纪律而非结构保证。
- **依赖图跨计划开放**（Q5）：耦合计划、破坏「计划=执行/跟踪单位」。
- **单文件与树双格式并存**（Q6）：两套代码路径、「何时用哪个」歧义。
- **group 可作委派单位**（Q7）：subagent 须导航子树、execute/track 逻辑分叉、复杂度上升。

## Consequences

- `skills/lib/plan-format.md` **重写**为树状格式契约。
- `plan-create` / `plan-execute` / `plan-track` 三 skill **全部适配**：
  - `plan-create`：按功能分解为 group/leaf 树，写 `plan.md` + 各级 `INDEX.md` + leaf 文件。
  - `plan-execute`：遍历树找就绪 leaf（todo 且 depends 满足）、执行、写 leaf 状态、向上刷新祖先 group 的 `INDEX.md`（roll-up）与计划根进度；全叶子 done 且 acceptance 满足 → 整目录移入 `completed/`。
  - `plan-track`：读 `plan.md` + 跨树汇总 leaf 统计、就绪 leaf、阻塞链、逐 group roll-up、树进度。
- 旧**单文件格式退役**（本仓库无存量计划，迁移成本为零）。
- 顶层 `docs/plan/INDEX.md` 形态不变（扁平计划注册表），仅每行进度语义改为「叶子完成比」。
