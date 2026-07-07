# Skills 质量评估综合报告

| 项目 | 内容 |
|---|---|
| 评估对象 | `.omp/skills/` 下 7 个 skill：docs-workspace、grilling-me、grilling-with-context、plan-create、plan-execute、plan-track、use-docs |
| 评估日期 | 2026-07-07 |
| 方法 | 7 skill × 每个 2 个测试员 subagent（共 14 个，各自隔离临时目录真实执行）→ 7 个**全新独立**评估员 subagent（回 skill 原文逐条复核测试员发现，剔除误判、补充遗漏） |
| 证据 | 14 份测试报告 `/tmp/skill-eval/report-*.md` ＋ 7 份评估报告 `/tmp/skill-eval/eval-*.md` ＋ 隔离执行产物 `/tmp/skilltest-*/` |
| 隔离性 | 全部测试在 `/tmp/skilltest-*` 完成，真实项目文件（`.omp/skills/`、`docs/`、`CONTEXT.md`）零改动 |

---

## 一、评估方法说明

**两段式、角色分离**：

1. **测试员（14 个，每 skill 2 个）**：在隔离临时目录里**真实执行** skill——该建文件就建并 `cat` 核对，该盘问就模拟用户推进 3–6 轮，该跑验证就真跑。每个测试员针对一个 skill 跑两个**互补场景**：通常一个是"主路径/清晰输入"，一个是"边缘路径/模糊或异常输入"，以暴露不同维度的缺陷。交付物：结构化报告（执行过程 + 完成标准逐条核对 + 按严重度排序的缺陷 + 评分）。

2. **评估员（7 个，全新 subagent）**：**不重新执行**，而是只读复核——读 skill 原文 + 两份测试报告 + 执行产物，对测试员声称的每条缺陷**回到 skill/lib 原文核实**，判定「确认成立 / 部分成立 / 误判」，并主动补缺。这一步的价值在于：测试员会误判（本报告记录了若干典型误判），评估员是纠偏层。

**为什么角色分离**：测试员既当 agent 又当模拟用户，容易"自己造问题再归咎"；评估员只看证据 + 原文，判断更客观。本评估中评估员修正的最典型误判是——**用方法论 skill（grilling-with-context）的标准去苛责一个有意极简的姿态型 skill（grilling-me）**。

---

## 二、评分总览

| Skill | 测试员 A | 测试员 B | 评估员终评 | 评级 |
|---|---|---|---|---|
| docs-workspace | 7 | 7 | **6.0** | 可用，边界稳定性不足 |
| grilling-me | 4 | 5 | **6.0** | 可用的极简姿态声明，有结构性缺陷 |
| grilling-with-context | 7 | 6 | **7.0** | 闭环扎实，兜底不对称 |
| plan-create | 8 | 7 | **7.0** | 主流程通，招牌场景兜底缺 |
| plan-execute | 7 | 7 | **7.0** | 核心机制通，状态转换与安全阀有缺口 |
| plan-track | 7.5 | 7 | **7.5** | 招牌检测生效，报告侧留白 |
| use-docs | 7 | 7 | **6.0** | 导航核心可用，自洽性有根本裂痕 |

**全局结论**：7 个 skill 的**核心主路径全部跑通**——14 个测试场景均执行到终态并产出符合 `plan-format.md` 等契约的产物（两个执行到 `done`/归档、一个到 `blocked`、多个产出完整计划树/术语表/ADR）。扣分集中在三类：**边缘路径兜底缺失、内部一致性、逐字契约缺失**。没有"不可用"的 skill；最弱的是 grilling-me（极简定位下仍欠自声明）和两个 6 分 skill（docs-workspace 的静默失败陷阱、use-docs 的自打耳光）。

---

## 三、各 Skill 详细评估

### 3.1 docs-workspace（终评 6/10）

**测试场景**
- A：全新空仓库（git init，无任何 docs/src），单上下文初始化。
- B：部分存在 + 多上下文 monorepo（已有 `docs/spec/existing-prd.md`、`src/ordering`+`src/billing`、`.git`、既有 `.gitignore`）。

**执行结果**：两场景均产出完整工作区（5 子目录 + 各 INDEX + CONTEXT + plan 骨架），完成标准 §7 基本逐条达成。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 严重 | **`.gitignore` 推荐 pattern 全文缺失，最自然的裸写法即错且静默失败** | §7 要求"保留其 INDEX.md"但无逐字 pattern。**实测**：测试员 B 产物用裸 `docs/generated/`，`git check-ignore` 命中 → INDEX.md 被忽略、`git add -n` 拒绝，**直接违反 §7**，而测试员 B 自评还误判为 ✅。最自然的写法就是错的，失败无声。 |
| 中偏高 | `docs/plan/INDEX.md` 两段空表骨架无逐字模板 | 三处要求"骨架"全指向 plan-format.md，但该文件只给带示例行的注册表，且两表**列数不同**（进行中 6 列 / 已完成 4 列）。测试员 A 首版即把 4 列配成 5 格分隔符。 |
| 中 | §7 完成标准漏列"各模块 CONTEXT.md" | 与 §2 多上下文结构图（含 `src/ordering/CONTEXT.md`）冲突——严格按 §7 验收会漏建模块 CONTEXT.md。 |
| 中 | `plan-format.md` 是唯一未加"执行时先 read"指令的被引用 lib | 其余三份 lib（index/context/adr）都显式写了"——执行时先 read 该文件"，唯独 plan 没有，引用约定内部不一致。 |
| 中 | CONTEXT.md "init 即建"（§7）与 lib "首个术语确立才建"（context-format L59）口径不一 | init 阶段该建多空的 CONTEXT.md 未明。 |
| 中 | "INDEX 已存在但 stale"无处理条款 | 与"不覆盖""先索引后正文"三边冲突；既有项目（本 skill 自述适用场景）的 INDEX 极可能 stale。 |
| 轻 | 单/多上下文"兜底按单上下文"规则只在 §7 | 空仓库场景（DW-A）会触发一次本可避免的人机往返。 |

**改进建议**
- **P0**：内联 `.gitignore` 逐字 pattern `docs/generated/*` + `!docs/generated/INDEX.md`，注明"勿用裸 `docs/generated/`"；内联 plan/INDEX 两段空表骨架（6 列 / 4 列各一份）。
- **P1**：§7 多上下文条目补"各上下文目录各一份 CONTEXT.md"；§3/§4 引用 plan-format.md 处补"先 read"对齐；§5 显式化解 CONTEXT 冲突（init 种占位骨架）。
- **P2**：§4 加 stale INDEX 处理条款（仅增量编辑）；§2 补 `packages/`/`apps/` 模块 CONTEXT 落点 + 多上下文判定正反例小表。

---

### 3.2 grilling-me（终评 6/10）

**测试场景**
- A：模糊计划"我要做一个通知系统"，无任何细节。
- B：含 3 处内部矛盾的设计草案（部分取消 vs 整单不可拆；不可逆 vs 15min 撤回；职责未定义）。

**执行结果**：两场景均推进 4–6 轮盘问，矛盾被压出。但两位测试员打了低分（4、5）。

**关键澄清：测试员基准错配**
两位测试员的低分主因是**用 grilling-with-context 的方法论标准去衡量一个有意极简的姿态型 skill**——他们要求补"设计树维度清单""矛盾施压四动作""Open Questions 路由表""完成标准段"。评估员判定这些**应驳回**：那属于隔壁 grilling-with-context 的职责，强加等于把 grilling-me 变成 g-w-c 的副本，破坏刻意设计的两层结构。剔除基准错配后，与"极简"无关的真实结构性缺陷有 3 条：

| 严重度 | 不足 | 证据 |
|---|---|---|
| 严重 | **不自声明与 grilling-with-context 的分工** | "纯盘问不落盘"只写在兄弟 skill g-w-c 文本里（其 line 3/10），grilling-me 自身通篇未提。这是两位测试员大量"应补"误判的**根源**。 |
| 严重 | 收尾协议缺失 | line 12 只有"共识前别动工"的负面指令，无"达成共识后产出摘要 / 交还下一步"的正面流程。 |
| 中 | `name: grilling` 与目录 `grilling-me` 不一致 | frontmatter line 2 vs 目录名错位，可能影响调度命中并与同仓 skill 在 name 空间冲突。 |
| 轻 | "设计树"核心术语从未定义也未链接 | line 6 用它作指令主语却默认 agent 都懂。 |
| 轻 | 无最小范式问答示例 | 目录仅 SKILL.md，无 references。 |

**误判清单（评估员驳回）**：docs 无 fallback、代码库无 fallback（均为条件句/前置检查的正常语义，不需要显式 else）；"一个问题"颗粒度（测试员自造歧义）；先复述计划（外部方法论强加）；维度清单/矛盾动作/路由表/完成标准段（属 g-w-c 职责）。

**改进建议**
- **P0**：加一句边界自声明（"只盘问不落盘，需沉淀转 grilling-with-context"）+ 一句收尾协议（共识后给摘要+未决项+交还下一步）+ 修 `name`。一句话可消除约 60% 误判。
- **P1**：定义"设计树"一词 + 加 1 个最小范式问答（3–4 行）。
- **不建议**：照搬 g-w-c 的 §2/§3/完成标准段。

---

### 3.3 grilling-with-context（终评 7/10）

**测试场景**
- A：术语会结晶的设计（给计划系统加"计划模板"功能），可能触发 ADR。
- B：docs 工作区未就位（没跑 docs-workspace）。

**执行结果**：A 真实写入 CONTEXT.md（新增 2 术语+关系+3 Open Questions）+ ADR（proposed，含 Options/Consequences）+ 同步 INDEX；ADR 克制原则（三条标准）被真实定义并执行（R4 因"易回退"主动跳过 ADR）。B 演示了 catch-22。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 中-高 | **docs 子目录兜底与 CONTEXT.md 不对称（catch-22 真实成立）** | §0.1 唯独给 CONTEXT.md 开"懒创建"兜底，对 docs/spec/adr/reference 一字未提；§3 又要求"当场写、不积压"。在"未跑 docs-workspace + agent 继续 + 结晶出 spec/ADR 级知识"这条边缘路径上，字面派 agent 落入"违反 §3 积压 / 违反不做什么 自建"两难。**主路径无碍**（A 场景全程畅通即证），故中-高非严重。 |
| 中 | §3 路由表缺"目录/放置约定"目的地 | 新产物类型无处可去，被迫污染 CONTEXT.md Open Questions（A 实测违反 context-format 的 Open Questions 契约）。 |
| 中 | spec 路由无"够格写"阈值 | 与 ADR 三条件不对称——CONTEXT/ADR/Open Questions 都给了触发线，唯独 spec 没有。 |
| 中 | "遍历设计树"无分支枚举/穷尽法 | 完成标准"每分支被盘问"不可客观核验，依赖 agent 经验。 |
| 中（补充） | 单→多上下文演进迁移未覆盖 | 盘问中途中浮现第二个独立模块时，如何首次创建 CONTEXT-MAP、把根级模块专属术语迁出，skill 未说。 |
| 轻 | ADR"提议"vs"落盘"Status 流向未点破 | §3 已给方向（落盘与否由用户定），ambiguity 真实但轻微。 |

**误判澄清**：B 的 catch-22 真实成立但严重度被高估（主路径不撞，且宽容路径有合法解读）；B 自身演示的"半残树"部分是其应用不一致（建了子目录却不建父级 docs/INDEX.md）。

**改进建议**
- **P0**：§0.1 加兜底总则——可为本 skill 即将写入的单个目标目录懒创建目录+同级 INDEX+父级 docs/INDEX 登记，**不**批量初始化、**不**配 .gitignore。
- **P1**：§3 路由表补"目录/放置约定"目的地；§3 spec 行补阈值；§1 补最小分支发现启发式（概念定义/关系模型/生命周期/存放索引/命名碰撞/边缘场景六类）；§3 行 61 补单→多上下文迁移步骤。
- **P2**：点破 ADR 提议/落盘 Status 流向；adr-format 编号补"空目录从 0001 起"。

---

### 3.4 plan-create（终评 7/10）

**测试场景**
- A：清晰目标（给 plan-track 加 `--json` 输出选项）→ 全流程分解。
- B：模糊目标"优化整个系统性能"→ 必须先盘问。

**执行结果**：两场景均产出严格符合 plan-format.md 契约的计划目录（Dotted ID 与路径一致、group INDEX 派生状态正确、预计触碰文件=leaf files 并集、顶层 INDEX 加行、leaf 均 ≤5 文件、标签词表用对）。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 中 | **招牌场景缺"盘问收敛失败"明文出口** | 模糊目标是 plan-create 核心入口（description 明写"先用 g-w-c 盘问"），但盘问后目标仍过宽/不可分解时，skill 从未明文说"缩小范围 / 拆前置计划 / 标 draft+[BLOCKER]"。出口机制其实存在（draft+blocker+五项强制，B 的产物实证可兜），但缺指引让 planner 靠"精神"推断。 |
| 中 | 引用路径三种基点混用 | `skills/*`（根相对）、`references/*`（skill 相对、未声明）、裸名。读者须猜 `references/` 归属；同一仓库内 plan-format.md 引用 mode-selection 却用全路径，风格不统一。 |
| 轻→中 | decomposition.md 尺寸表 off-by-one | 5 同时落 M(3-5，直接做) 与 L(5-8，拆) 两档且处置相反，与 SKILL.md "≤5"直接冲突，影响 §3 分解决策。 |
| 轻-中 | 无源码/纯规划场景退化未声明 | §2 三项动作（glob/grep/lsp）对早期项目或纯文档规划悬空。 |
| 轻 | 检查点对 ≤3 leaf 小计划无指引 + 命名歧义 | 三处一致只说"每 2-4 leaf"，2-leaf 计划该设几个未说。 |
| 轻 | verification 对纯文档/指令类 leaf 缺说明 | §6"复制到 bash 验一次"面向代码，改 .md 的 leaf 只能 grep。 |

**误判澄清**：A 称"references 标签大小写切换未点破"为误判——§1 line 25 原文已写"frontmatter 存为小写"。B 把"目标不可分解"定为"严重"过激——出口实际兜住了（B 自己的产物即用 draft 出口）。

**改进建议**
- **P0**：新增"§1.x 盘问收敛失败处置"小节，明文三出口（缩小范围/拆前置计划/标 draft+[BLOCKER]），并把 §8 draft 框定扩到"或目标层面未定型"。
- **P1**：统一引用基点（全用相对 skills 根全路径，或 §0 显式声明 references 基点）；修尺寸表 L 下界为 6-8；声明无源码退化路径。
- **P2**：小计划检查点指引；verification 适用范围（文档类可用 grep/手动遵循）；grilling 深度随目标清晰度缩放。

---

### 3.5 plan-execute（终评 7/10）

**测试场景**
- A：react 模式全叶子成功 → 归档（给假项目加 README）。
- B：leaf 反复失败 → replan/blocked（verification 注定失败）。

**执行结果**：A 真实跑通 leaf 循环 + roll-up + 整目录归档（active/ 空、completed/ 有目录、顶层 INDEX 挪行、复盘笔记完整）；B 跑通 react→重试 2 次→判定计划级缺陷→leaf+plan 双 blocked→roll-up 刷新两层 group INDEX→blocked 计划留 active。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 中 | **`plan.status: ready→in_progress` 转换全程缺席**（每次执行都踩） | SKILL/modes/replan 三文均无触发点，只能由 plan-format 词表推断；§3 step5 只刷"进度列"不刷"状态列"（比 plan-format 生命周期表窄）。两位测试员都是"自行推断"补做。每次执行都让顶层 INDEX 状态列失真。 |
| 中 | replan 决策可复现性差 + 安全阀失效 | replan.md §2/§3 判别"目标仍合理"靠主观裁量，且 SKILL §5 速览**省略了该前提**（只读速览者倾向误判进 §2）。收敛上限（replan≥3 次）**无 replan_count 字段载体**、"全局"scope（per-plan？per-leaf？）未定义 → §4 安全阀形同虚设。 |
| 中（补充） | §2 单数 in_progress 假设在 subagent/hybrid 中断后续期失效 | 一个波次可并行多 in_progress，中断后 L51"该 leaf"（单数）无法决定继续哪一个；modes.md 未覆盖波次中断续期。 |
| 轻 | §2 就绪判定无 `plan.status` 闸门 | plan blocked 时 §2 仍可能取出另一个就绪 leaf 执行，与"plan blocked 应停止"冲突。 |
| 轻 | §2 路径式 Dotted ID 解析对违规计划无降级指引 | 合规计划上 §2 正确；测试员 A 的"落空"是其自造违规计划触发。 |
| 轻 | blocked 复盘笔记必填字段散落三处（SKILL §7 / replan §3 / 示例）不统一 | 无 blocked 条目字段模板。 |

**误判澄清**：A-3（§2 路径解析落空）——测试员 PE-A 计划本身违反 plan-format L234（直挂根 leaf 应单段 id 却写 1.1），§2 在合规计划上正确；A-4（roll-up 派生 todo）——共享契约设计，测试员自己已注明非 plan-execute 独有；B-5（verification 可达性前置检查）——对一般命令不可判定，2 次重试已是安全网，属过度设计。

**改进建议**
- **P0**：§3 step1 显式加"首次置 leaf in_progress 时同步 `plan.status: ready→in_progress`"；§3 step5 改为"进度列与状态列"；plan.md frontmatter 加 `replan_count` 字段并定义 scope（per-plan）。
- **P1**：§5 速览第 2 分支补"目标仍合理、leaf 边界不变"前提 + "§5 出错必读 replan.md 全文"；replan.md §2/§3 补客观判据；§2 补 subagent/hybrid 多 in_progress 续期规则。
- **P2**：§2 ID 解析补"frontmatter id 为声明真源，路径用于校验，不一致即计划违规"；§6 step4 明示"丢弃状态/进度/模式列"；补 blocked 复盘字段模板。

---

### 3.6 plan-track（终评 7.5/10）

**测试场景**
- A：3 个计划（done/in_progress/blocked）+ 故意 drift（幽灵目录、缺记、谎报派生状态、自相矛盾行）。
- B：深嵌套 3 层 group + 混合叶子状态 + 注入 3 处 roll-up drift。

**执行结果**：A 定位全部 4/4 drift + 零写入（14 文件 sha256 一致）；B 定位全部 3/3 roll-up drift + 1 个就绪 leaf（含 group 依赖解析）+ 零写入（15 文件 sha256 一致）。§2 七项汇报齐全。

**核心设计判断（任务点名复核）**：track 把 roll-up 规则"委托"给 plan-format.md **是合理的**——§0 强制预读 + 三 skill 共享单一契约 + 实证（两位测试员都正确算出递归 roll-up）。**不应在正文重述整表**。但正文术语会误导，需一行消歧。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 中-高 | **drift 报告侧（招牌能力）几乎留白** | §1/§2 反复要求"标 drift"，但 §5 输出格式只定义默认视图，**全文无 drift 小节的位置/格式/标记约定**。drift 是 track 区别于"读 plan.md"的招牌能力，检测 mandated 但呈现完全留白。drift 也无严重度分级（blocked 计划缺记 vs group 状态小误同等对待）。 |
| 中 | 委托术语会误导 | line 36"子节点"在直接子节点 vs 递归后代间歧义；line 32"done group"在 drift 语境下可能被误读为 INDEX 声明值（恰 drift 时算错就绪判定）。 |
| 中 | §4 概念性 flag 呈现与语义 | 无真实 CLI 时过滤视图输出形态未规范；`--status blocked` 未区分 plan 级 vs leaf 级（plan=in_progress 含 blocked leaf 即触发歧义）。 |
| 中（补充） | 检查点"已过"判定规则缺失 | 复选框 `[ ]` 状态 vs leaf-status 重算，未规定以哪个为准；B 场景复选框未勾但 group 实际全 done，track 无调和规则。 |
| 中（补充） | drift 无严重度分级 | 高危（blocked 计划缺记）与低危（group 状态小误）同等对待。 |
| 轻 | "无 todo 但有 in_progress"下一步无指引 | 常见真实状态（A 直接命中），字面"下一步"为空，而用户要的是"在跑的那个 leaf"。 |

**误判澄清**：B-D3（roll-up 优先级 track 不复述）为误判——委托设计的应有之义，B 自己也用对了；B-D1/B-D2 的"严重"定级偏重（实证均跑通，缺口为一行消歧/格式规范）。

**改进建议**
- **P0**：新增"§Drift 报告"节——判定口径（含 INDEX 缺/多记、目录缺 plan.md、group 派生状态≠重算、group 进度分子分母≠重算、顶层 INDEX 进度数字≠真源）+ 严重度分级（blocked/abandoned 计划缺记=严重）+ 呈现（默认视图末尾单列，按严重度排序，每条给"位置+期望 vs 实际+建议动作"）。
- **P1**：§2 line 36 改为"按递归全部后代叶子重算"并交叉引用；line 32"done group"补"group 依赖满足 ⇔ 递归叶子全 done，以叶子 frontmatter 为真源不看可能漂移的 INDEX 行"；line 34"checkpoint 已过"补判定规则。
- **P2**：§4 开头声明 flag 为用户意图（无真实 CLI，产出过滤视图）；明确 `--status` 作用域；显式声明工具集（仅 read/glob/grep，禁 edit/write/bash 写）。

---

### 3.7 use-docs（终评 6/10）

**测试场景**
- A：5 个导航查询（状态词表 / Leaf Task 术语 / 架构决策 / 计划进度 / INDEX 格式），全程只读真实 docs。
- B：4 个写入意图（建 PRD / 改 CONTEXT.md / 初始化工作区 / 改计划状态），验证只读 + 重定向。

**执行结果**：A 的 5 查询几乎全部正确路由，全程只读（md5 一致）；B 的 4 请求均未写入（before/after md5+mtime+find 三重证据），R3→docs-workspace、R4→plan-execute/track 路由干净。**但发现自洽性根本裂痕**。

**确认的核心不足**

| 严重度 | 不足 | 证据 |
|---|---|---|
| 严重 | **自洽性裂痕——references 重述了它发誓"绝不重述"的 lib** | skill 把"绝不重述 lib"作为定义性承诺重复 4 次（frontmatter/§0/§10/不做什么），但自己的 `references/context-structure.md` **逐字照抄** lib 的"判定依据"规则（diff 证实 L24 ≡ context-format.md L90，仅前缀/加粗不同），并用 lib 模板的相同字段名 + 相同领域示例（Order/Customer/Money）复述段落骨架与术语归属规则。`docs-structure.md` L114-120 同样复述 index-format 纪律。**以"不重述"为身份的 skill 自打耳光**——这是评估员比两位测试员各低 1 分的主因。 |
| 严重 | 写入重定向地图不完整 | 术语写入的正确 skill `grilling-with-context` 在 SKILL + 两份 references **0 次出现**（grep 证实）。CONTEXT.md/术语是 use-docs 核心解释对象，却不知术语由谁写入。 |
| 中 | §0 把只读 lib 误列为"写内容"出口 | §0"或对应格式契约（写内容）"会让 agent 误以为去 index-format.md 就能完成 PRD 写入。§0/§4/不做什么 三处写入出口表述不一致（lib vs skill vs 仅 docs-workspace）。 |
| 中（补充） | docs-structure.md L30-36 静态维护 lib 文件清单本身是 drift 表面 | 与 skill"单一真源"论自矛盾——lib 新增/删除一个 *-format.md，此清单即漂移。 |
| 中-轻 | §2 plan 行未拆"查进度→plan-track"vs"写/推进→plan-execute" | 字面只让读 docs/plan/INDEX.md（看板），可能拿到已 drift 的值。 |
| 轻 | "格式"一词不覆盖词表/规则 | Q1"状态词表"严格说是受控词表非"格式"，§2 表无匹配行。 |

**误判澄清**：B 称"不修改约束埋底部"为误判——L8 intro 与 §0 已双重醒目声明"全程只读""不创建、不修改任何文件"，非埋底。

**改进建议**
- **P0**：references 改纯指路——`context-structure.md` 删除"判定依据"整句与所有领域示例，段落降级为骨架名清单+"见 context-format.md 模板"；`docs-structure.md` L114-120 改"INDEX 通用纪律见 index-format.md#规则"。补 `grilling-with-context` 重定向（§0 与 §2 路由表各加"修订/新增术语 → g-w-c"）。
- **P1**：§2 拆 plan 行为"查进度→plan-track（只读对账）""写/推进→plan-execute"；§2"确切格式"扩为"格式/词表/规则"；§2 增"写 spec/reference/ADR 内容：本仓库无专用 skill，由人或对应工作流写"；§0 修正写入出口（lib 标注"只读，不代替写入"）。
- **P2**：正文点名 4 个 lib 文件名；§4.1 完成标准补"或定位到所需 lib 契约"；docs-structure.md lib 清单改"read skills/lib/ 目录获取"；§0 加程序护栏（工具调用应只有 read/grep/glob/ls）。

---

## 四、跨 Skill 共性问题（系统级）

### 4.1 逐字契约缺失（"点名形状但不给文本"）
- **表现**：docs-workspace 的 .gitignore、plan/INDEX 空骨架；plan-execute 的状态转换。skill 反复"先 read lib"，但 lib 只给带示例的模板，空形态要 agent 自己删行，出错率高（列数错配可复现）。
- **建议**：凡被要求产出的"骨架/空表/逐字 pattern"，在 lib 或 skill 内联一份删净示例的版本。

### 4.2 跨文件引用基点不统一
- **表现**：plan-create 的 `skills/*` vs `references/*` vs 裸名；plan-format.md 自身引用 mode-selection 也用全路径；docs-workspace 对 plan-format.md 唯独不加"先 read"。
- **建议**：全仓统一"相对 skills 根"全路径，或在每个 skill §0 显式声明 references 基点。

### 4.3 "委托给 lib"合理，但正文术语会误导
- **表现**：plan-track 把 roll-up 委托给 plan-format.md 合理（§0 强制预读 + 单一真源 + 实证），但正文"子节点""done group"在 drift 语境下会自我击败。
- **建议**：委托保留，但在正文每个易误读术语处补一行交叉引用/消歧，**而非内联复制整表**。

### 4.4 兜底/降级路径不对称
- **表现**：grilling-with-context 只给 CONTEXT.md 懒创建不给 docs 子目录；plan-create 只给自检失败的 draft 出口不给"目标不可分解"出口；grilling-me 只给负面指令（别动工）不给正面收尾。
- **建议**：每条"主路径"都配平"边缘路径/失败路径"的明文处置。

### 4.5 自声明边界缺失导致误用误评
- **表现**：grilling-me 不自声明与 g-w-c 分工；use-docs 不知术语由谁写入。
- **建议**：每个 skill 自声明定位 + 兄弟 skill 边界，避免被误用误评。

---

## 五、优先修复路线图

### P0（投入产出比最高，多为 1–2 句文本，建议立即修）

| Skill | P0 修复 | 价值 |
|---|---|---|
| docs-workspace | 内联 `.gitignore` 逐字 pattern（含 negation）+ plan/INDEX 两段空表骨架 | 消灭**实测**的静默失败 + 列数错配 |
| grilling-me | 加边界自声明 + 收尾协议 + 修 `name` | 一句话消除约 60% 误判 |
| grilling-with-context | §0.1 加 docs 子目录懒创建兜底总则 | 消除 catch-22 |
| plan-create | 新增"盘问收敛失败处置"小节（三出口） | 兜住招牌场景 |
| plan-execute | 显式 `ready→in_progress` 转换 + `replan_count` 字段 + §5 速览补前提 | 修每次执行都踩的真缺口 + 救活安全阀 |
| plan-track | 新增"§Drift 报告"节（格式 + 严重度分级） | 兑现招牌能力 |
| use-docs | references 改纯指路（删 lib 重述）+ 补 g-w-c 重定向 | 修复自洽性根本裂痕 |

### P1（内部一致性与方法补全，应修）
统一引用基点；docs-workspace §7 补模块 CONTEXT.md + plan-format "先 read" 对齐；plan-create 修尺寸表 off-by-one + 声明无源码退化；plan-execute 补客观 replan 判据 + 多 in_progress 续期；plan-track 正文术语一行消歧；use-docs §2 拆 plan 读/写行 + lib 标"只读"；grilling-with-context §1 补分支发现启发式 + 单→多上下文迁移。

### P2（精度与体验，宜修）
小计划检查点指引；verification 文档类适用范围；blocked 复盘字段模板；use-docs 点名 4 lib 文件名 + 程序护栏；plan-track §4 flag 作用域规范化。

---

## 六、对各评估报告的信任度说明

- 评估员对测试员的复核产出了若干**误判标记**（已在上文各 skill 节列出），最显著的修正：
  - **grilling-me**：测试员 A/B 的 4、5 分偏低，主因基准错配；其"应补维度清单/矛盾动作/路由表"建议被驳回。
  - **docs-workspace**：测试员 B 对 .gitignore 的 ✅ 系事实性误判（产物实测违反 §7）。
  - **plan-execute**：测试员 A 的"§2 路径解析落空"是其自造违规计划触发，§2 在合规计划上正确。
  - **plan-track**：测试员 B 的"track 必须重述 roll-up 语义"判为误判（委托设计应有之义，B 自己也用对了）。
- 因此本综合报告以**评估员终评**为准，测试员原始评分仅作对照。

---

## 附录：证据索引

| 类型 | 路径 |
|---|---|
| 测试报告（14 份） | `/tmp/skill-eval/report-{DW-A,DW-B,GM-A,GM-B,GWC-A,GWC-B,PC-A,PC-B,PE-A,PE-B,PT-A,PT-B,UD-A,UD-B}.md` |
| 评估报告（7 份） | `/tmp/skill-eval/eval-{docs-workspace,grilling-me,grilling-with-context,plan-create,plan-execute,plan-track,use-docs}.md` |
| 执行产物 | `/tmp/skilltest-*/`（各 skill 的隔离执行目录，含生成的 docs/计划树/术语表/ADR 等） |
| 被测 skill 原文 | `.omp/skills/*/SKILL.md` + `.omp/skills/lib/*-format.md` + 各 skill 的 `references/` |

> 各 `/tmp/skill-eval/eval-*.md` 含逐条原文行号引用、测试员误判完整清单、P0/P1/P2 改后文本，可作为修复的直接依据。
