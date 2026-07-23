# 派生 JSON 结构

> 由 `scripts/context_manager.py parse` 从 CONTEXT.md 生成。**派生产物，不手改**——要改术语就改 CONTEXT.md 再重新 `parse`。
>
> 访问方式：`./references/json-schema.md` 或 `skill://context-system/references/json-schema.md`。

## 结构

```json
{
  "schema_version": "1.0",
  "context_name": "计划系统",
  "description": "本上下文覆盖 plan-create/plan-execute/plan-track 三 skill 共享的计划文件格式与任务分解模型。",
  "scope": {
    "in": ["计划的文件/目录结构", "任务的层级分解模型", "节点角色与状态"],
    "out": ["任务执行协议", "领域术语"]
  },
  "terms": [
    {
      "name": "Plan Tree",
      "definition": "一个计划不再是单个 .md 文件，而是镜像任务层级的文件/目录树。",
      "aliases": ["多文件计划", "树状计划"],
      "avoid": ["单文件计划", "flat plan"],
      "example": null,
      "see_also": ["Group Node", "Leaf Task", "Plan Manifest", "Dotted ID"],
      "status": "active",
      "source": "ADR-0001",
      "owner": null,
      "since": null,
      "anti_example": null
    }
  ],
  "relationships": [
    "一个 Plan 是一棵 Plan Tree 的根",
    "一个 Group Node 包含零或多个 Group Node 与 Leaf Task"
  ],
  "open_questions": [
    { "text": "「退款」是 Order 的状态，还是独立的聚合？", "status": "unresolved" }
  ],
  "parsed_from": "CONTEXT.md",
  "parsed_at": "2026-07-23T12:00:00+00:00"
}
```

## 字段说明

| 字段 | 层 | 类型 | 缺失时 |
|---|---|---|---|
| `name` / `definition` | 核心 | str | definition 缺失 → validate 报「缺定义」 |
| `aliases` / `avoid` / `see_also` | 核心 | list[str] | `[]` |
| `example` | 核心 | str | `null` |
| `status` | 扩展 | str（draft/active/deprecated） | `null`；非空须合法，否则 validate 报「Status 非法」 |
| `source` | 扩展 | str | `null` |
| `owner` / `since` / `anti_example` | 更可选 | str | `null` |

## 校验约束（validate 据此检查）

- **重复术语**：`terms[].name` 不重复。
- **悬空 See also**：`see_also` 中的每个名字须存在于某 `terms[].name`，否则报悬空。
- **Aliases 冲突**：`aliases` 中的值不得等于任何 `terms[].name`（主词），否则报冲突。
- **Status 合法**：非 null 时须 ∈ {draft, active, deprecated}。
- **Open Questions**：无 `[status]` 标记的条目默认 `unresolved`。
