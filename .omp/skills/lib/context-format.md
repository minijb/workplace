# CONTEXT.md 格式

`CONTEXT.md` 是限界上下文的**术语表**，用于在人与人、人与 LLM 之间对齐通用语（ubiquitous language）。它**只描述概念是什么，不描述如何实现**——规格归 `docs/spec/`，决策归 `docs/adr/`。

## 文件结构

每个限界上下文目录放一份 `CONTEXT.md`。单上下文仓库放在根目录；多上下文仓库在根目录同时放一份**项目级共用术语表** `CONTEXT.md`（跨上下文通用概念）与一份 `CONTEXT-MAP.md`（上下文清单与关系），并在每个上下文目录各放一份 `CONTEXT.md`（见文末）。

## 模板

```md
# {上下文名称}

{一两句话说明：这个上下文负责什么、为什么单独存在、它的边界在哪。}

## Scope

- **In**: {本上下文管辖的概念/能力，如「下单、订单状态机、取消」}
- **Out**: {显式声明不属于本上下文的内容，如「支付、库存、物流」}

## Language

### Order

{一两句话定义「是什么」。}
- **Aliases**: {同一概念的其他叫法，选其中一个作主词}
- **Avoid**: {明确不要使用的近义词，避免歧义}
- **Example**: {最小实例帮助快速对齐，如「用户一次性购买 3 件商品生成的一个订单」}
- **See also**: {关联术语，如 Customer、LineItem}

### Customer

下单的人或组织；一个 Customer 可拥有多个 Order。
- **Aliases**: 账户持有人
- **Avoid**: Client, buyer, account
- **See also**: Order

## Relationships

{术语之间的关系速览，用于一眼看清模型骨架。}

- 一个 **Customer** 拥有多个 **Order**
- 一个 **Order** 包含多个 **LineItem**
- **Order** 经取消流程进入 `Cancelled` 状态

## Open Questions

{尚未达成共识、待澄清的术语，列出以免被遗忘。}

- 「退款」是 Order 的状态，还是独立的聚合？
- 「取消」是否区分用户取消与系统取消？
```

## 规则

- **只写术语**：仅收录本上下文特有的概念；通用编程概念（超时、错误类型、工具模式）不入内。加词前自问：这是本上下文独有的概念，还是通用编程概念？只有前者入内。
- **要武断**：同一概念有多个词时，选定一个作主词，其余列入 `Aliases` 或 `Avoid`。
- **定义紧凑**：每个术语一两句话，说清「是什么」而非「做什么」。
- **随用随写**：术语被确定时**立即**更新，不要积压；文件仅在首个术语确立时创建。
- **不含实现**：不写技术选型、数据结构、接口签名——这些归 `docs/spec/` 或 `docs/adr/`。
- **关系即骨架**：用 `Relationships` 一句话勾勒模型，帮助快速建立心智模型。
- **悬而未决要可见**：未定术语写入 `Open Questions`，避免被默默忽略。
- **术语只归一处**：每个术语只写在一个地方——能跨多个上下文通用的归**根级** `CONTEXT.md`，仅属某上下文的归**该模块**的 `CONTEXT.md`；不重复定义，必要时用 `See also` 互链。

## 单上下文 vs 多上下文

- **单上下文（多数仓库）**：根目录一份 `CONTEXT.md`，承载全部术语。
- **多上下文（多模块 / monorepo）**：根目录同时放 `CONTEXT.md`（**项目级共用术语**，跨上下文通用的概念，如 `Money`、`CustomerId`、`Tenant`）与 `CONTEXT-MAP.md`（上下文清单与关系）；每个上下文目录内再各放一份 `CONTEXT.md`，仅收录该上下文专属术语。

> **项目级 CONTEXT.md 与模块级模板的差异**：上述 `## 模板` 是为**单一限界上下文**（模块级）设计的——`Scope: In/Out` 列该上下文的领域边界。**根级（项目级共用）`CONTEXT.md`** 跨多个上下文，`Scope` 应写「跨上下文通用的概念（如共享值对象、ID 类型、租户模型）」而非某一模块的领域；若项目级尚无明确共用术语，`Scope` 可省略或仅写一句话边界。其余段落（`Language` / `Relationships` / `Open Questions`）结构不变。**不要为凑模板杜撰术语**——项目级 CONTEXT.md 可只含标题与一两句说明，术语随用随写（见「规则·随用随写」）。

`CONTEXT-MAP.md` 模板：

```md
# Context Map

项目级共用术语见 [./CONTEXT.md](./CONTEXT.md)；下列为各限界上下文。

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — 接收并跟踪订单
- [Billing](./src/billing/CONTEXT.md) — 生成发票并处理支付
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理拣货与发货

## Relationships

- **Ordering → Fulfillment**: Ordering 发布 `OrderPlaced`，Fulfillment 消费以开始拣货
- **Fulfillment → Billing**: Fulfillment 发布 `ShipmentDispatched`，Billing 消费以开票
- **Ordering ↔ Billing**: 共享 `CustomerId` 与 `Money` 类型
```

> 判定依据：仓库内有多个相互独立、各自具备完整领域语义的模块（如 `src/ordering`、`src/billing`）即为多上下文；仅是分层（`controllers/services/models`）仍属单上下文。无法判断时询问用户。
