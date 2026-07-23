# 如何书写并评价一个 Skill —— 深度方法报告

> 撰写日期：2026-07-23
> 方法：4 个 subagent 并行调研（3 联网 + 1 读本地）+ 主 agent 综合，并以本工作区 7 个 skill 为实证
> 性质：方法论报告（只读调研，未改动任何运行时文件）
> 配套：本报告的评价部分（PCSAID 框架）已在 `grilling-me-评价报告.md` 中对一个真实 skill 做过实证检验

---

## 导读（TL;DR）

1. **skill 的本质**：被 LLM/agent 按需加载、规约其在特定场景下行为的「知识 + 指令」包。它不是文档，而是**一段会持续消耗注意力预算、并决定执行体行为的活代码**。
2. **写 skill 的核心矛盾**：入口精简（省 token）↔ 自包含（可执行）。解药是**渐进式披露**——但 2026 年的实证研究给出反直觉结论：披露「买的是上下文，不是智能」，且**递归多级披露有害，一层 flat 足够**。
3. **评 skill 的核心立论**：评 skill ≠ 评文档美观，而 = 评「**加载它之后，执行体能否正确、可靠、高效达成目标，且不越界、不退化**」。必须从「加载后行为」倒推。
4. **最高杠杆动作**：写好 `description`（决定 skill 是否被触发，是承重墙）；区分「事实 vs 过程」（决定该写 rule 还是 skill）；贯彻单一真源（防漂移）。
5. **一句话纪律**：目标是每次**复现同一过程**而非同一输出（predictability）；每段指令须对应一个**真实观测到的失败模式**，否则是裁剪对象。

---

## 第一章 什么是 Skill —— 本质、边界与业界三范式

### 1.1 定义

一个 skill 是**一个目录**，至少含一个 `SKILL.md`：以 YAML frontmatter（`name` + `description`）开头，后接 Markdown 正文，并可在同级 `references/`、`scripts/`、`assets/` 下承载按需加载的长内容、可执行脚本与模板 [agentskills.io 规范]。

广义上，凡「被 LLM/agent 按需加载、规约其在特定场景下行为的知识+指令包」都是 skill——含 SKILL.md / Cursor Rules / AGENTS.md / system prompt 片段 / SOP 知识包。

### 1.2 业界三范式：规则 vs 技能

三大主流范式在「Markdown 载体、YAML frontmatter 触发、渐进式披露、单一真源、500 行/5000 token 上限、命令式书写」六点完全**共识**；分歧集中在触发机制：

| 范式 | 载体 | 触发机制 | 本质定位 |
|---|---|---|---|
| **Agent Skills** (Anthropic) | `SKILL.md` + frontmatter | description **语义匹配**（模型决定加载） | **技能**（on-demand 能力） |
| **Cursor Project Rules** | `.cursor/rules/*.mdc` | 四模式：always / auto-glob / agent-requested / manual | 混合（可常驻可按需） |
| **AGENTS.md** (开放标准) | 纯 Markdown，无 schema | **无触发**，靠文件路径就近性 | **规则**（always-on 上下文） |

> **关键判据——事实还是过程**（Anthropic）：常驻的「事实/约定/构建命令」写进 AGENTS.md/CLAUDE.md；多步骤「过程/检查清单/SOP」才抽成 skill。**一旦 CLAUDE.md 的某段「长成了过程而非事实」，就该移出做成 skill。** [code.claude.com/docs/en/skills]

这映射到两条路线之争的本质：**规则（常驻上下文）** vs **技能（按需能力）**。本工作区的 `.omp/rules/`（用 `globs` 路径触发）与 `.omp/skills/`（用 `name+description` 语义触发）正是这对分工的本地物化。

### 1.3 核心张力预告

整份报告围绕一个张力展开：**入口精简（省 token / 抗 context rot）↔ 自包含（可执行 / 抗漏触发）**。第二章讲如何用渐进式披露平衡它，第四章讲它何时会失衡。

---

## 第二章 如何书写一个 Skill

### 2.1 结构：一个目录 + 三类资源

```
skills/<skill-name>/
├── SKILL.md          # 入口：门面与索引，不是内容容器
├── references/       # 只读长内容：模板、格式规范、完整示例
└── scripts/          # 可执行：校验/生成/转换脚本
```
- 目录名即 skill 名；资源与 SKILL.md 同级，不散落到 skill 目录外 [rule://skill-progressive-disclosure]。
- 跨 skill 共享的资料放 `skills/lib/` 并用相对 skills 根的全路径引用；**skill 自身专属内容必须在自身目录内**。

### 2.2 frontmatter：name + description 是「身份证」

`description` 是模型判断**何时触发该 skill 的唯一依据** [Anthropic]。Anthropic 反复强调「Pay special attention to the name and description — Claude will use these when deciding whether to trigger the skill」。

**好坏对照**（来自规范）：
- ✅ `Extracts text and tables from PDFs, fills PDF forms, and merges PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`
- ❌ `Helps with PDFs.`（含糊→不被触发）

**本地三段式范本**（本工作区成熟 skill 一致采用）：`做什么` + `何时用（含触发词/场景）` + `边界声明（不做什么、归哪个兄弟 skill）`。例：`plan-create` 末句「不执行任务——执行归 plan-execute，进度查询归 plan-track」[.omp/skills/plan-create/SKILL.md]。

> **承重墙证据**：Zhang et al.（2026）审计 138,000 个公开 SKILL.md，结论「valid metadata is what makes a skill reliably retrievable」——元数据有效性直接决定可检索性 [arXiv:2607.17598 §2.2]。description 写不好→发现阶段不匹配→**skill 永不加载→静默遗漏**。

### 2.3 骨架：统一六段式（本地实证，6/7 遵循）

本工作区最稳定的书写模式：

```
引言（主旨一两句）
→ ## 0. 前置（读契约 / 建现状心智模型 / 工具护栏）
→ ## 1..N 编号流程小节
→ 收敛段
→ ## 完成标准（可观测）
→ ## 不做什么（重定向表）
```

证据：grilling-me / grilling-with-context / plan-create / plan-execute / plan-track / use-docs 均如此 [.omp/skills/*/SKILL.md]。唯一偏离者是 `docs-workspace`（无显式 §0、无「不做什么」段）——是工作区内最显著的待改进点。

**写格式类 skill 的硬护栏**：所有会落盘固定格式的 skill，§0 第一步设「**禁止凭记忆写格式**，每次先 read 真源契约」。这是针对 LLM「凭记忆写、易漂」弱点的硬约束——plan-create/execute/track、grilling-with-context 全部如此 [.omp/skills/plan-create/SKILL.md §0]。

### 2.4 渐进式披露：三层结构与「何时内联 vs 下沉」

业界共识的三层加载（Anthropic）：

| 层 | 内容 | 量级 | 何时进上下文 |
|---|---|---|---|
| ① 发现 | name + description | ~100 tokens | 启动时常驻 |
| ② 激活 | SKILL.md 正文 | <5000 tokens / <500 行 | 模型判定相关时 |
| ③ 执行 | references/scripts/assets | 按需 | 用到时才读 |

**「何时内联 vs 何时下沉」决策树**（综合本地规则 + Anthropic structure-for-scale）：

```
这段内容是「每次都要先理解才能开始」的核心步骤/完成标准/反模式？
 ├─ 是 → 内联进 SKILL.md（即使略长）
 └─ 否（按需查阅/互斥分支/外部规范全文/完整模板）→ 下沉 references/scripts
     └─ 多个分支任一次只用其一？→ 拆成 N 个文件（比合 1 个更省 token）
```

本地规则给出硬判据：「若一段内容是『执行流程中按需查阅』而非『每次都要先理解才能开始』，它就该外置」；正文超约 150 行、或含完整模板/长脚本即外置化 [rule://skill-progressive-disclosure]。

> **反直觉的实证**（arXiv:2607.17598，2026-07 首篇受控研究，∞Bench 跨 3 harness/3 模型族）：
> 1. **披露「买的是上下文，不是智能」**——对强导航 agent 在单文档上增益近零，库级语料才决定性（Codex raw 在 K=20 本时 En.QA 崩到 0.26，flat 守住 0.46）。
> 2. **递归多级（hierarchical）披露有害，一层 flat 足够**——没有任何格子奖励额外深度；Pi 上 gpt-5.4-mini 的 En.MC 从 flat 的 **0.91 崩到 0.64**。原因：「always-loaded child descriptions saturate the router's context before it commits to a chunk」。
> 3. **人工策展有效，模型自动生成无效**——SkillsBench（Li et al. 2026）：「curated packs lift performance while model-authored packs add nothing」；Huang（2026）：LLM 写的 skill「每一节都在自我争辩」。
>
> **推论**：①信息架构**不是越深越好**，一层 flat 是默认；②skill 的下沉/分层结构应由人或从文档结构固定，**不能让模型整段生成**。

### 2.5 单一真源 + 引用基点

- 共享格式/规则只定义一次，放独立文件（`skills/lib/*-format.md` 或共享 model-invoked skill），正文「写入前先 read 该文件」，**只指路不复述整表**。
- 引用基点统一并**显式约定**：本 skill 专属用 `./references/`、跨 skill 共享用 `skills/lib/` 全路径；路径歧义处补一句「引用基点约定」消歧（范本：plan-create §0 唯一显式声明者）[.omp/skills/plan-create/SKILL.md]。
- **例外**：「空骨架/逐字 pattern」允许在 skill 内联一份删净示例的版本，但完整模板仍在真源——这是渐进式披露与单一真源之间精确的边界划分 [.omp/skills/lib/plan-format.md]。

### 2.6 边界声明 + 边缘/失败路径配平

- **「不做什么」= 重定向表**：每条「不 X——归 Y skill」，让边界自文档化、撞到边界即知转哪。这是本工作区边界声明的范本级实践 [.omp/skills/grilling-with-context/SKILL.md]。
- **兄弟关系用顶部 blockquote 声明**：plan-create/execute/track 顶部「> 三 skill 关系」+「> 核心模型」固化共享心智模型 [.omp/skills/plan-create/SKILL.md]。
- **每条主路径配平边缘/失败路径**：给客观判据、重试与升级上限（如重试 ≤2、replan ≤3）、降级兜底；失败分支下沉 references 时，正文留一棵决策树速览并指向全文。范本：plan-execute §5 replan 决策树 [.omp/skills/plan-execute/SKILL.md]。

### 2.7 命令式书写 + leading word + 可预测性

- **命令式**：陈述「做什么」而非叙述「怎么做/为什么」。skill 加载后其内容跨轮常驻，**每一行都是反复发生的 token 成本** [code.claude.com/docs/en/skills]。
- **leading word**（mattpocock）：挑一个已存于预训练的紧凑概念词（如 tight/red/tracer bullet）同时锚定执行与触发，并「hunt restatements that a single word can retire」（猎杀可被一词退役的重述）。
- **可预测性是根本美德**（mattpocock）：「A skill's job is to wrangle determinism out of a stochastic system, so the goal is not the same output every run but the same **process**.」——每个书写决策都问「是否让行为更可预测」，而非「是否更完整/更聪明」[aihero.dev/skills-writing-great-skills]。

### 2.8 书写红线（反模式清单）

- ❌ 把整份模板/格式规范/脚本源码内联进 SKILL.md。
- ❌ description 含糊（`Helps with X.`）或只写「做什么」不写「何时用」。
- ❌ 写「详见某文件」却不给路径（盲猜失败），或给绝对路径/仓库外路径。
- ❌ 跨 skill 复制粘贴同一段长内容——抽到 `lib/` 或共享 skill 单点维护。
- ❌ 把 skill 专属资源放到 skill 目录之外。
- ❌ 为极少触发的边缘情况开 skill；起点从简、按需扩张（Cursor 官方 anti-pattern）。
- ❌ 让模型整段生成 skill 结构（实证：无效甚至有害）。

---

## 第三章 如何评价一个 Skill —— PCSAID 框架

### 3.1 评价的本质

> 评价一个 skill ≠ 评判文档写得是否美观，而 = 评判「**加载该 skill 之后，执行体能否正确、可靠、高效地达成 skill 声明的目标，且不越界、不退化**」。

三条推论：①从「加载后的可观测行为」**倒推**；②每条结论须**有证据、可判定、可操作**；③必须考虑**退化风险**——执行体的天然倾向（一次多做、替用户决策、凭记忆写）会在哪里压垮约束。

### 3.2 六维 PCSAID

| 维度 | 判定焦点 | 典型反模式 |
|---|---|---|
| **P 定位与触发** | description 准确刻画场景与触发词？自声明与兄弟边界？ | 边界模糊、触发词重叠歧义、与同类 skill 职责交叉 |
| **C 内容与方法论** | 核心方法有真源/自洽？分类 MECE？流程闭环？ | 分类重叠或遗漏、流程缺收敛/验收、方法无依据 |
| **S 结构与渐进式披露** | 入口精简自包含？何时加载明示？单一真源？ | 入口塞细节、关键节从未挂载、同一内容多处重复 |
| **A 可执行性与遵从度** | 指令可判定？完成标准可观测？硬约束无破口？退化有锚点？ | 含糊指令、不可观测完成标准、对天然倾向无对抗 |
| **I 一致性** | 入口↔下沉、验收↔流程、术语统一？ | 同一规则两处不一、术语漂移 |
| **D 工程纪律** | 硬约束全程无破口？遵守工作区契约？ | 声称只读却隐含写入 |

**评分**：每维 0–5；权重 A/C 各 25%、P 20%、S/I/D 各 10%；加权→0–100→等级（≥85 优秀 / 70–84 良好 / 55–69 合格 / <55 待改进）。

> 该框架已对真实 skill（grilling-me）做过实证：5 视角并行评审，综合 75/100，详见 `grilling-me-评价报告.md`。

### 3.3 评价方法谱系：三层，缺一不可

业界对 prompt/skill 评价已形成三层（Braintrust / Mirascope）：

| 层 | 评什么 | 方法 | 适用 |
|---|---|---|---|
| **(A) 静态 rubric 评审** | 指令文本本身 | 人工按维度打分（清晰度/具体性/结构/角色/示例） | 改前快速筛查，无需测试数据 |
| **(B) 数据集客观 eval** | 产出在代表性输入上达不达标 | golden set + LLM-as-judge + 回归门禁 | 可复现、可作 CI 门禁 |
| **(C) 行为/对抗测试** | 真实分布与对抗下鲁棒性 | 边界用例、注入、pairwise、A/B、在线 eval | 守长尾与安全 |

任一单独都不充分。**PCSAID 属于 (A)**——它是改前最快、门槛最低的筛查；但它必须与 (B)(C) 互补：rubric 评「写得好不好」，eval 评「跑得对不对」，行为测试评「崩不崩」。

### 3.4 skill 评价 vs 一次性 prompt eval 的关键差异

业界**尚无针对「可复用 agent skill」的成熟评价框架** [EvalMethods 调研缺口]。一次性 prompt eval 只测「固定输入→产出」单点映射；可复用 skill 必须额外度量 5 个独有维度：

| skill 独有维度 | 一次性 prompt 是否覆盖 | 含义 |
|---|---|---|
| **触发正确性** | ❌ | 该加载时是否加载、不该加载时是否克制 |
| **边界与作用域** | ❌ | 声称覆盖的场景是否真覆盖、是否越界 |
| **跨场景泛化** | 部分 | 超出作者预期分布的输入上是否脆化 |
| **token 经济性** | ❌ | 价值密度（高信号/低 token），因长上下文退化 |
| **可维护/可组合** | ❌ | 改一处牵几处、与他 skill 共存是否冲突 |

> **推论**：评 skill = prompt eval（测加载后 I/O）∪ context engineering 判据（测指令包设计）∪ 激活/边界/泛化（skill 独有）。

### 3.5 关键经验证据（评价的机理基础）

1. **Lost in the Middle**（Liu et al. 2023，被引 5297+）：模型对长上下文注意力呈 **U 型**——相关信息位于**首尾**时性能最高、**居中显著退化**，即便显式长上下文模型亦然 [arXiv:2307.03172]。**含义**：评长 skill 时，关键信息位置会系统性影响其被遵守度——这不是质量问题，是位置问题。
2. **Context Rot**（Chroma 2025，18 个 SOTA 模型）：即便任务复杂度恒定、只变输入长度，性能也**非均匀退化**；干扰项与低相似度放大退化 [research.trychroma.com/context-rot]。**含义**：skill 不能无限堆 token——每加一个 token 都在消耗注意力预算。
3. **机理**：transformer 的 n² 两两注意力随上下文变长被「拉薄」，且训练数据短序列更常见——退化是「gradient 而非 cliff」，更隐蔽 [Anthropic context engineering]。
4. **质量≠孤立指标**：一个把 relevance 提 5% 却让 token/延迟翻倍的 prompt 未必是净改进；对反复加载的 skill，成本按「每次调用 × token × 频次」累积 [Braintrust]。

### 3.6 评价流程（7 步，可复现）

1. **读全**：frontmatter + 正文 + 全部 references + 其引用的 lib 契约（核实真单一真源）。
2. **提取契约**：自声明的【目标】【完成标准】【不做什么】【边界】——验收基线。
3. **六维逐评**：每项给【证据（引用原文）】【评分】【改进】。
4. **交叉一致性**：入口 vs 下沉、完成标准 vs 正文流程、术语统一。
5. **真源核对**：若声称改编外部方法，**联网核对忠实度与增删得失**。
6. **退化推演**：站执行体视角枚举「可能在哪里悄悄偏离」，检查锚点。
7. **产出**：六维评分表 + 优点 + 关键问题（按严重度）+ **优先级改进清单（P0/P1/P2）**。

---

## 第四章 深度专题：Skill 设计的关键张力

每个张力给判定准则——这是把「清单」升格为「判断力」的部分。

### 4.1 入口精简 ↔ 自包含（渐进式披露的核心矛盾）

**张力**：入口精简省 token、抗 context rot；自包含防漏触发、保证完成标准可自查。

**何时失衡——Dunning-Kruger 缺口**：条件加载触发器写成「不确定是否穷尽时再 read」是**自指条件**——尚未加载框架的 agent 恰恰无法意识到自己可能漏（不知道自己不知道）。后果链：跳过加载 → 不知道关键清单 → 完成标准引用未具体化概念 → 凭即兴宣布完成 → 穷尽判据失效。（实证：grilling-me 的条件加载触发器即犯此病，见 `grilling-me-评价报告.md`。）

**判定准则**：
- **完成标准所必需的内容，必须内联**（即使略长）——否则完成标准无法自查。
- 把「必备清单」当必备，不当可选深度；条件加载触发器避免自指（要么默认加载，要么把精简清单内联入口）。

### 4.2 always-on ↔ on-demand（cognitive load vs context load）

**张力**（mattpocock）：每个 skill 必然花掉认知负荷或上下文负荷之一——model-invoked 每轮把 description 留窗口里（花 context load，但自动触发）；user-invoked 剥掉 description（零 context load，但靠人记住，花 cognitive load）。

**判定准则**：
- 按「事实 vs 过程」分流：常驻事实→AGENTS.md/CLAUDE.md；多步过程→skill。
- 当 user-invoked skill 多到记不住时，引入一个 **router skill** 点名其余 skill 及各自何时用。

### 4.3 可预测性 ↔ 完整性

**张力**：追求完整/聪明 vs 追求可复现的过程。

**判定准则**（mattpocock）：每个书写决策问「是否让行为更**可预测**」，而非「是否更完整」。用四组诊断失败模式——premature completion（过早完成）/ duplication（重复）/ sediment（沉积）/ sprawl（蔓延）/ no-op（空操作）；对每句施以 single-source-of-truth、relevance、**no-op test**（这句话拉动行为吗？不拉动就删）。

### 4.4 约束强度 ↔ 灵活（right altitude）

**张力**：硬编码 if-else（脆弱、维护贵）↔ 模糊高阶指导（信号不足、错误假设共享上下文）。

**判定准则**（Anthropic context engineering）：system prompt 应处在 **right altitude**——「足够具体以引导行为、又足够灵活以提供强启发式」。minimality ≠ 尽量短，而是「能完整勾勒期望行为的最小信息集」。迭代法：**先用最小 prompt 跑最强模型看裸表现，再按观测到的失败模式增量补指令与示例**——无失败模式支撑的规则是裁剪对象。

### 4.5 通用 ↔ 特化（单一真源 + 双前门）

**张力**：一个能力被多个场景需要时，复制 vs 抽象。

**判定准则**（mattpocock）：把共享逻辑抽成 model-invoked 的**单一真源引擎**，为它开多个 user-invoked **前门**（一个引擎、两个入口）。例：grilling 引擎 + grill-me / grill-with-docs 两个前门。本工作区的 grilling-me / grilling-with-context 正是这对双前门的本地实现。「The language lives in one place, and everything that needs it points there.」

---

## 第五章 检查清单与模板

### 5.1 书写检查清单（Write Checklist）

- [ ] 一个目录 + SKILL.md；frontmatter 含 `name`（与目录同名）+ `description`。
- [ ] description 三段式：做什么 + 何时用（含触发词/场景，用**用户的原话**）+ 边界声明。
- [ ] SKILL.md 是「目录页 + 流程」而非内容容器；正文 < 500 行 / < 5000 token。
- [ ] 完成标准所必需的核心步骤/清单**内联**；按需查阅内容下沉 references/scripts。
- [ ] 每处外置资源给**可机械定位的相对路径** + 「何时 read 的判定条件」。
- [ ] 「不做什么」= 重定向表，每条指向具名接管 skill。
- [ ] 每条主路径配平边缘/失败路径（判据 + 重试上限 + 降级兜底）。
- [ ] 完成标准**可观测**（能跑的命令 / 可枚举状态值 / 可验证行为）。
- [ ] 共享格式抽到单一真源，正文只指路不复述。
- [ ] 命令式书写；逐句过 no-op test（不拉动行为就删）。
- [ ] 写格式类 skill：§0 设「禁止凭记忆写格式」+ 先 read 契约。
- [ ] 只读 skill：显式声明工具护栏（允许/禁用工具清单）。

### 5.2 评价检查清单（Review Checklist，PCSAID 展开）

- [ ] **P**：description 能否独立让用户/选择器在触发词重叠时正确分流？是否与兄弟 skill 双向回指？
- [ ] **C**：核心方法有真源？分类 MECE 且按领域可裁剪？流程闭环（前置→执行→收敛→完成标准）？
- [ ] **S**：references 每节都被入口挂载？入口摘要是否忠实预览下沉细节（而非另一套分类）？条件加载触发器是否自指？
- [ ] **A**：完成标准无需加载 reference 即可自查？硬约束有可观测外部表征？退化风险有锚点？
- [ ] **I**：入口与下沉对同一概念的表述一致？术语统一？验收项在正文都有对应？
- [ ] **D**：硬约束（只读/不落盘/一次一题）全程无破口？符合工作区契约？
- [ ] **退化推演**：站执行体视角，枚举 3+ 条「可能悄悄偏离」的路径，检查锚点。

### 5.3 SKILL.md 最小模板

```markdown
---
name: my-skill              # 与目录同名，小写连字符
description: <做什么>. <何时用，含触发词>. <边界：不做什么、归哪个兄弟>.
---

# <Skill 名>

<一句话主旨：做什么、何时用>

## 0. 前置
- 读真源契约：执行前先 read `skills/lib/xxx-format.md`（禁止凭记忆写格式）。
- 建现状心智模型：glob/grep 涉及的既有上下文。

## 1. <流程步骤一>
... 遇到长内容时：见 `./references/xxx.md`——<何时 read 的判定>。

## 收敛
<复述关键结论 + 未解决冲突显式标注>

## 完成标准
- <可观测项：能跑的命令 / 可枚举状态值 / 可验证行为>

## 不做什么
- 不 X——归 <兄弟 skill>。
```

---

## 第六章 本地实证：本工作区 7 skill 的范本与反例

> 这一章证明上述方法论不是空中楼阁——本工作区已沉淀出高度一致的书写纪律，可作为范本对照。

### 6.1 范本（值得复制的实践）

| 实践 | 范本位置 |
|---|---|
| 统一六段式骨架 | 6/7 skill 遵循 [.omp/skills/*/SKILL.md] |
| description 三段式 | plan-create / grilling-me / plan-track |
| 「禁止凭记忆写格式」护栏 | plan-create/execute/track、grilling-with-context §0 |
| 显式「引用基点约定」消歧 | plan-create §0（唯一显式声明者） |
| 单一真源 lib/*-format.md | 4 份契约被多方引用、单点维护；references 显式「不重述」 |
| 「不做什么」= 重定向表 | grilling-with-context / plan-execute / grilling-me |
| replan 决策树 + 收敛上限 | plan-execute §5 + references/replan.md |
| 自检步骤（对照真源逐项核查） | plan-create §6 Plan-Validate |
| 只读 skill 工具护栏 | plan-track §0 / use-docs §0（显式允许/禁用工具） |
| 路由决策用表格 | grilling-with-context §3 / use-docs §2 |
| references 自包含（标题+适用范围+加载触发） | grilling-technique.md / decomposition.md 等 |

### 6.2 反例 / 待改进（实证「方法论的敌人」）

| 反例 | 位置 | 违反 |
|---|---|---|
| docs-workspace 缺「不做什么」段、无显式 §0、description 无边界声明 | .omp/skills/docs-workspace/SKILL.md | 骨架一致性、边界声明 |
| 路径双写（`skills/lib/` 与 `../lib/` 并存） | docs-workspace §4/5/6 | 引用基点统一 |
| 六类分支清单重复（grilling-with-context 内联 vs grilling-technique.md 真源） | grilling-with-context §1 | 单一真源 |
| 条件加载触发器自指（「不确定是否穷尽时 read」） | grilling-me §1 | Dunning-Kruger 缺口（§4.1） |
| references §3/§4 从未被入口挂载 | grilling-me | 渐进式披露挂载 |

---

## 附录：参考来源

**业界规范与厂商**
- Agent Skills 开放规范：https://agentskills.io/specification
- Anthropic 工程博客（Agent Skills）：https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic（Skills Explained）：https://claude.com/blog/skills-explained
- Claude Code Skills 文档：https://code.claude.com/docs/en/skills
- Anthropic context engineering：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic《6 Techniques for Effective Prompt Engineering》(PDF)
- Cursor Rules：https://cursor.com/docs/rules
- AGENTS.md 开放标准：https://agents.md/

**实证研究**
- 渐进式披露受控研究：arXiv:2607.17598（§2.2 引 Zhang et al. 2026 审计 138k SKILL.md；§2.2 引 SkillsBench Li et al. 2026、Huang 2026；§5.1 Depth does not pay）
- Lost in the Middle：arXiv:2307.03172（Liu et al. 2023）
- Context Rot：https://research.trychroma.com/context-rot（Chroma 2025）

**评价方法**
- Braintrust prompt evaluation：https://www.braintrust.dev/articles/what-is-prompt-evaluation
- Mirascope prompt evaluation：https://mirascope.com/blog/prompt-evaluation
- Anthropic Console eval（SDTimes 报道）

**mattpocock 设计哲学**
- writing-great-skills：https://www.aihero.dev/skills-writing-great-skills
- domain-modeling / grill-with-docs：https://www.aihero.dev/skills-domain-modeling ；https://www.aihero.dev/skills-grill-with-docs
- skills 体系解读：https://explainx.ai/blog/matt-pocock-agent-skills-real-engineers
- 仓库：https://github.com/mattpocock/skills

**本地实证（本工作区）**
- `rule://skill-progressive-disclosure`（.omp/rules/）
- `.omp/skills/{grilling-me,grilling-with-context,plan-create,plan-execute,plan-track,use-docs,docs-workspace}/SKILL.md`
- `.omp/skills/lib/{plan,context,adr,index}-format.md`
- 配套实证报告：`grilling-me-评价报告.md`（PCSAID 框架对一个真实 skill 的 5 视角评审）

---

*本报告由 4 个并行 subagent（librarian×3 联网 + scout×1 读本地）产出原始调研，主 agent 按 PCSAID 框架综合，并以本工作区 7 个 skill 为实证。所有外部结论均附来源 URL；本地结论均附文件路径。调研全程只读，未改动任何运行时文件。*
