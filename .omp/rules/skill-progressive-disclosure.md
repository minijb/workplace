---
description: 创建或修改 skill 时采用渐进式披露——SKILL.md 保持整洁精简，仅承载入口说明与流程；模板、长示例、脚本、参考资料等下沉到 skill 同级 references/ 与 scripts/ 子目录，按需以 skill://<name>/<path> 加载。
globs:
  - "**/skills/**/SKILL.md"
  - "skills/**/SKILL.md"
  - "**/SKILL.md"
---

# Skill 渐进式披露（Progressive Disclosure）

## 1. 适用范围

凡**创建新 skill 或修改既有 skill**（`SKILL.md` 及其同目录资源）时，必须遵守本规则。被触发或读取本规则后，先按本规则校验目标 skill 的结构与 `SKILL.md` 篇幅，再动手写入。

## 2. 核心原则

`SKILL.md` 是 skill 的**门面与索引**，不是内容容器。它必须做到：

- **入口精简**：一眼能看清「这个 skill 做什么、何时用、按什么流程执行」。
- **延迟加载**：长内容（模板、格式规范、完整示例、脚本、外部参考资料）**不下沉到 SKILL.md 正文**，而是落到同级子目录，并在正文用一句话指明「执行时先 `read` 该文件」。
- **指路明确**：每处外置资源都标注相对路径（如 `./references/xxx.md` 或 `skill://<name>/scripts/xxx.sh`），让 agent 能机械定位、无需盲猜。

> 判据：若一段内容是「执行流程中按需查阅」而非「每次都要先理解才能开始」，它就该外置。

## 3. 标准目录结构

每个 skill 独占一个目录，遵循如下布局：

```text
skills/<skill-name>/
├── SKILL.md              # 入口：名称、描述、流程、对外置资源的引用
├── references/           # 长内容：模板、格式规范、调研笔记、完整示例
│   ├── template-*.md
│   └── format-*.md
└── scripts/              # 可执行：校验脚本、生成脚本、辅助工具
    └── *.sh / *.py / *.mjs
```

要点：

- **每个 skill 一个目录**，目录名即 skill 名（`name` 缺省时取目录名）。
- **资源与 SKILL.md 同级**，不要散落到 skill 目录之外；不要把内容塞进一个扁平的 `lib/`。
- 跨 skill 共享的资料可放在 skills 根级公共目录（如 `skills/lib/`）并用 `../lib/xxx.md` 引用，但**该 skill 自身专属的内容必须在本 skill 目录内**。

## 4. SKILL.md 内容分配

`SKILL.md` **只保留**：

| 区块 | 内容 |
|---|---|
| frontmatter | `name`、`description`（**必填**，决定能否被发现与匹配）；按需 `globs`、`alwaysApply`、`hide` |
| 一句话主旨 | 这个 skill 做什么、何时该用 |
| 执行流程 | 编号步骤，每步说清「做什么」；遇到长内容时**指向外置文件**而非内联 |
| 外置资源清单 | 一句话列出 `references/`、`scripts/` 下各文件及其用途，供 agent 按需加载 |
| 完成标准 | 可观测的验收条件 |

`SKILL.md` **不放**：完整模板正文、超长代码块、逐字示例、可执行脚本源码、外部规范全文。

## 5. references/ 与 scripts/ 的使用约定

### references/（只读长内容）

- 命名用业务语义：`adr-format.md`、`index-template.md`、`context-format.md`。
- 每个 `references/*.md` 自带标题与「适用范围」说明，可独立阅读。
- 在 `SKILL.md` 流程中引用时，写明「执行时先 `read` 该文件」并给出相对路径，例如：
  > 格式与规则见 `./references/index-template.md`——执行步骤 4 时先 `read` 该文件。

### scripts/（可执行）

- 仅放真正需要在执行流程中**运行**的脚本（校验、生成、转换、统计）。
- 脚本须带用法注释（shebang、入参、产物路径）。
- 在 `SKILL.md` 中写明调用方式与产物去向，不要把脚本源码贴进正文。

### 访问方式

- 项目内引用：相对路径 `./references/xxx.md`、`./scripts/xxx.sh`。
- 跨会话/协议引用：`skill://<skill-name>/references/xxx.md`（`skill://` 协议会拒绝绝对路径与 `..` 穿越，资源必须落在 skill 目录内）。

## 6. 操作清单（创建/修改 skill 时）

1. **扫描现状**：先 `glob`/`read` 目标 skill 目录，确认是否已存在 `references/`、`scripts/`。
2. **体检 SKILL.md**：若正文已超过约 150 行，或包含完整模板/长脚本，**外置化**到对应子目录，SKILL.md 仅留指路说明。
3. **新建 skill**：按 §3 结构一次性创建 `SKILL.md` + 必需子目录；frontmatter 的 `description` 必填。
4. **迁移既有内容**：把 SKILL.md 中「按需查阅」类长内容剪切到 `references/`，可执行内容剪切到 `scripts/`，原位替换为一句话引用。
5. **同步引用**：确保 SKILL.md 中每处外置资源路径正确、描述一致；新增/删除文件时同步更新 SKILL.md 的资源清单。
6. **自检**：SKILL.md 读起来像「目录页 + 流程」而非「内容大全」；每个 `references/`、`scripts/` 文件都能在 SKILL.md 中找到指路说明。

## 7. 反模式（避免）

- ❌ 把整份模板、整段格式规范、整段脚本源码直接内联进 `SKILL.md`。
- ❌ 把 skill 专属资源放到 skill 目录之外（如随意堆到仓库根的 `docs/` 或 `templates/`）。
- ❌ 在 `SKILL.md` 里写「详见某文件」却不给路径，或给绝对路径/仓库外路径。
- ❌ 一个 skill 把资源塞进多个并列目录（如 `templates/`、`examples/`、`docs/` 并存）——统一用 `references/` 承载长内容、`scripts/` 承载可执行内容。
- ❌ 跨 skill 复制粘贴同一段长内容到各自 `SKILL.md`——抽取到 `skills/lib/` 共享或各自 `references/` 单点维护。
