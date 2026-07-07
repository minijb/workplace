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

> 单 / 多上下文的判定依据（含「无法判断时询问用户」）见 `skills/lib/context-format.md` 末段，本文件不重述。

## CONTEXT.md 段落结构（骨架名）

一份 `CONTEXT.md` 由以下段落组成——这里只列骨架名，**确切字段 / 示例 / 写法见 `skills/lib/context-format.md` 模板**，本文件不重述：

1. **标题 + 一句话**：这个上下文是什么。
2. **Scope**：本上下文管什么（In）、不管什么（Out）。
3. **Language**：术语表主体，每术语一个子节。
4. **Relationships**：术语之间的关系速览。
5. **Open Questions**：尚未达成共识、待澄清的术语。

## CONTEXT-MAP.md（仅多上下文）

根级 `CONTEXT-MAP.md` 是上下文清单与关系图，由两段组成（模板见 `skills/lib/context-format.md`）：

- **Contexts**：各限界上下文的路径 + 一句话说明。
- **Relationships**：上下文之间的集成关系。

文件开头通常指向根级 `CONTEXT.md` 作为项目级共用术语的入口。

## 术语归属规则（避免重复）

每个术语只写一处：跨上下文通用 → 根级 `CONTEXT.md`；仅属某上下文 → 该模块 `CONTEXT.md`。**归属规则原文（含示例与「术语只归一处」）见 `skills/lib/context-format.md#规则`**，本文件不重述。

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

- 确切模板、规则与单 / 多上下文判定原文 → `skills/lib/context-format.md`（只读参考）。
- **修订 / 新增术语**（写内容）→ `grilling-with-context`（边盘问边把术语落进 `CONTEXT.md`、决策入 `docs/adr/`）；仅搭术语表骨架 → `docs-workspace`。

本文件只做结构与归属的导航解释，不重述模板、不执行写入。
