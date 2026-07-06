# CONTEXT 结构（术语表系统）

`CONTEXT.md` 与 `CONTEXT-MAP.md` 的结构解剖。本文件是 `use-docs` skill 的术语表附录，**只读、只解释**——确切模板与规则见 `skills/lib/context-format.md`。

## 适用范围

供需要搞清「术语表放哪、长什么样、单上下文还是多上下文、术语该归哪一份」时查阅。`docs/` 工作区目录结构见 `./docs-structure.md`。

## CONTEXT.md 是什么

`CONTEXT.md` 是限界上下文的**术语表**（ubiquitous language），用于在人之间、人与 LLM 之间对齐通用语。

- **只描述概念是什么，不描述如何实现**——规格归 `docs/spec/`，决策归 `docs/adr/`。
- **只收录本上下文特有的概念**；通用编程概念（超时、错误类型）不入内。
- **不是草稿、不是规格**——它只固化已确立的「词是什么意思」。

## 放在哪里：单上下文 vs 多上下文

| 仓库形态 | 根级 | 模块级 |
|---|---|---|
| **单上下文**（多数） | 一份 `CONTEXT.md`，承载全部术语 | 无 |
| **多上下文**（多模块 / monorepo） | `CONTEXT.md`（**跨上下文通用术语**）+ `CONTEXT-MAP.md`（上下文清单与关系） | 每个上下文目录内各一份 `CONTEXT.md`（该上下文专属术语） |

**判定依据**（摘自 `skills/lib/context-format.md`）：仓库内有多个**相互独立、各自具备完整领域语义**的模块（如 `src/ordering`、`src/billing`）即为多上下文；仅是分层（`controllers/services/models`）仍属单上下文。无法判断时询问用户。

## CONTEXT.md 段落结构

一份 `CONTEXT.md` 由以下段落组成（确切模板见 `skills/lib/context-format.md`）：

1. **标题 + 一句话**：上下文名称 + 这个上下文负责什么、边界在哪。
2. **Scope**：
   - **In**：本上下文管辖的概念 / 能力（如「下单、订单状态机、取消」）。
   - **Out**：显式声明不属于本上下文的内容（如「支付、库存、物流」）。
3. **Language**（术语表主体）：每个术语一个子节。
   - 定义：一两句话说清「是什么」（不是「做什么」）。
   - **Aliases**：同一概念的其他叫法，选其中一个作主词。
   - **Avoid**：明确不要使用的近义词，消歧义。
   - **Example**：最小实例，帮助快速对齐。
   - **See also**：关联术语（跨文件 / 跨上下文互链）。
4. **Relationships**：术语之间的关系速览，一句话勾勒模型骨架（如「一个 Customer 拥有多个 Order」）。
5. **Open Questions**：尚未达成共识、待澄清的术语——写下来避免被默默忽略。

## CONTEXT-MAP.md（仅多上下文）

根级 `CONTEXT-MAP.md` 是上下文清单与关系图，由两段组成（模板见 `skills/lib/context-format.md`）：

- **Contexts**：各限界上下文的路径 + 一句话说明（如 `[Ordering](./src/ordering/CONTEXT.md) — 接收并跟踪订单`）。
- **Relationships**：上下文之间的集成关系（如「Ordering → Fulfillment: 发布 OrderPlaced 事件」）。

文件开头通常指向根级 `CONTEXT.md` 作为项目级共用术语的入口。

## 术语归属规则（避免重复）

- **跨上下文通用的术语** → 根级 `CONTEXT.md`（如 `Money`、`CustomerId`、`Tenant`）。
- **仅属某上下文的术语** → 该模块的 `CONTEXT.md`。
- **每个术语只写一处**，不重复定义；必要时用 `See also` 互链。

## 什么不该进 CONTEXT.md

| 不该进 | 该去 |
|---|---|
| 技术选型、数据结构、接口签名 | `docs/spec/` 或 `docs/adr/` |
| 难逆决策与「为什么」 | `docs/adr/` |
| 功能需求、验收标准 | `docs/spec/` |
| 第三方 API / 规范引用 | `docs/reference/` |
| 通用编程概念（超时、错误类型） | 不入术语表 |
| 草稿、未成型的方案 | `docs/spec/` 或 Open Questions（若仅是待澄清术语） |

## 格式契约

确切模板、规则与单 / 多上下文判定原文见 **`skills/lib/context-format.md`**——本文件只做结构与归属的导航解释，不重述模板。
