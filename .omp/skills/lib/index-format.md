# INDEX.md 格式

`INDEX.md` 是 `docs/` 下每个目录（含 `docs/` 自身）的**文件索引**，登记该目录下所有文件或子目录的相对路径与一句话说明。它是人机进入目录时的「目录页」——**先读索引，再按需加载具体文件。**

## 适用范围

- `docs/INDEX.md`：登记子目录（spec / generated / reference / adr / **plan**）。
- 各子目录的 `INDEX.md`（`docs/spec/`、`docs/generated/`、`docs/reference/`、`docs/adr/`）：登记其下的具体文件。
- **`docs/plan/` 特例**：由计划系统托管，结构异于其他目录。顶层 `docs/plan/INDEX.md` 是扁平计划注册表（分 active/completed 段、带状态/进度列）；**每个计划本身是一个目录树**，树中每个 group 目录各有自己的 `INDEX.md`（直系子节点 + 派生状态）。两者格式均见 `skills/lib/plan-format.md`「INDEX.md 结构」。

## 模板（子目录，登记具体文件）

```md
# {目录名} 索引

本目录下文件的路径与一句话描述。新增/删除文件时同步更新。

| 路径 | 说明 |
|---|---|
| `./0001-event-sourced-orders.md` | 采用事件溯源建模订单的决策记录 |
| `./0002-postgres-write-model.md` | 写模型选用 Postgres 的决策记录 |
```

`docs/INDEX.md`（登记子目录）示例：

```md
# docs 索引

docs 子目录的相对路径与一句话说明。

| 路径 | 说明 |
|---|---|
| `./spec/` | 功能规格：PRD、需求、接口约定、验收标准 |
| `./generated/` | 工具/agent 生成的产物（已入 .gitignore） |
| `./reference/` | 外部知识：第三方 API 摘要、规范引用、调研笔记 |
| `./adr/` | 架构决策记录 |
| `./plan/` | 计划系统：`active/` 进行中、`completed/` 已完成，`INDEX.md` 为注册表 |
```

## 规则

- **先索引后正文**：进入任何 `docs/` 目录先读 `INDEX.md`，再按需加载具体文件——禁止在未读索引时盲猜文件名。
- **同步维护**：新增或删除文件时立即更新同级 `INDEX.md`，不要积压。
- **粒度**：`docs/INDEX.md` 登记子目录；各子目录的 `INDEX.md` 登记其下的具体文件。
- **一句话即可**：说明控制在一句以内，说清「是什么」，不展开实现。
- **相对路径**：路径以 `./` 开头、相对当前目录书写。
- `docs/generated/INDEX.md` 即使目录被 `.gitignore` 忽略也需维护，供 agent 当次会话定位产物。
