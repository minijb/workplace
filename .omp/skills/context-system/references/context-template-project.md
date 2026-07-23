# 项目级 CONTEXT.md 模板（跨上下文共用术语）

> **适用**：多上下文仓库的**根目录** `CONTEXT.md`，收录跨多个上下文通用的概念（共享值对象、ID 类型、租户模型等）。
>
> **与模块级的差异**：`Scope` 写「跨上下文通用的概念」而非某一模块的领域边界；若项目级尚无明确共用术语，`Scope` 可省略或仅写一句话边界。其余段落（Language / Relationships / Open Questions）结构不变。
>
> **不要为凑模板杜撰术语**——项目级 CONTEXT.md 可只含标题与一两句说明，术语随用随写。

---

```md
# {项目名} · 共用术语

{一两句话：本项目由哪些上下文组成，本文件收录跨上下文通用的概念。各上下文专属术语见各自模块级 CONTEXT.md。}

## Scope

- **In**: {跨上下文通用的概念，如共享值对象 Money、ID 类型 CustomerId、租户模型 Tenant}
- **Out**: {各上下文专属术语（归各自模块级 CONTEXT.md）}

> 若项目级尚无明确共用术语，本 Scope 可省略。

## Language

### Money

{跨上下文共享的金额值对象定义。}
- **Aliases**: 金额
- **Avoid**: price, cost（这些是上下文内的派生概念，不是共享值对象）
- **Example**: {「¥199.00」一个不可变的金额值对象}
- **See also**: CustomerId

<!-- 扩展层（可选）-->
- **Status**: active
- **Source**: ADR-0003 统一金额模型

## Relationships

{跨上下文的共享关系，如各上下文如何引用共享类型。}

- **Ordering** 与 **Billing** 共享 **Money** 与 **CustomerId** 类型
- **Tenant** 被所有上下文引用以做多租户隔离

## Open Questions

- [unresolved] Money 是否需要带币种，还是各上下文自行约束？
```

---

## 何时用项目级 vs 模块级

| 判据 | 用哪份 |
|---|---|
| 仓库只有一个领域（即使分层 controllers/services） | 单上下文：根目录一份**模块级** CONTEXT.md 即可 |
| 仓库有多个相互独立、各自完整领域语义的模块（monorepo） | 根目录一份**项目级** + 各模块各一份**模块级** + 根目录一份 CONTEXT-MAP.md |
| 某概念跨多个上下文复用（如 Money、Tenant） | 归**项目级** |
| 某概念仅属一个上下文 | 归**该模块级** |

> 判定依据：仓库内有多个相互独立、各自具备完整领域语义的模块即为多上下文；仅是分层仍属单上下文。无法判断时询问用户。
