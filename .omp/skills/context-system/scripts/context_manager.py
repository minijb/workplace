#!/usr/bin/env python3
"""
context_manager.py — 管理 CONTEXT.md 限界上下文术语表。

子命令：
  parse <path> [-o out.json]              解析 CONTEXT.md → JSON（派生索引）
  validate <path|dir>                     校验术语表质量
  query <path> <keyword|--status X>       查询术语
  generate-map <root> [-o CONTEXT-MAP.md] 多上下文：汇总各模块生成 Context Map

数据流：CONTEXT.md（真源，人/agent 写）→ parse → JSON（派生，不手改）。
仅依赖 Python 标准库。用法：python3 context_manager.py <cmd> ...
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
VALID_STATUS = {"draft", "active", "deprecated"}
LIST_FIELDS = {"Aliases", "Avoid", "See also"}
SCALAR_FIELDS = {"Example", "Status", "Source", "Owner", "Since", "Anti-example"}
SCALAR_KEY = {
    "example": "example", "status": "status", "source": "source",
    "owner": "owner", "since": "since", "anti-example": "anti_example",
}

H1 = re.compile(r"^#\s+(.+?)\s*$")
H2 = re.compile(r"^##\s+(.+?)\s*$")
H3 = re.compile(r"^###\s+(.+?)\s*$")
BULLET_FIELD = re.compile(r"^\s*-\s+\*\*(.+?)\*\*\s*:?\s*(.*)$")
BULLET_PLAIN = re.compile(r"^\s*-\s+(.+?)\s*$")
OQ = re.compile(r"^\s*-\s*\[(unresolved|resolved)\]\s*(.*)$", re.I)


def split_list(value: str) -> list[str]:
    if not value:
        return []
    return [p.strip() for p in re.split(r"[,，、;；]", value) if p.strip()]


def new_term(name: str) -> dict:
    return {
        "name": name, "definition": "",
        "aliases": [], "avoid": [], "example": "", "see_also": [],
        "status": None, "source": None, "owner": None,
        "since": None, "anti_example": None,
    }


def parse_context(text: str, source: str = "CONTEXT.md") -> dict:
    ctx = {
        "schema_version": SCHEMA_VERSION,
        "context_name": None, "description": "",
        "scope": {"in": [], "out": []},
        "terms": [], "relationships": [], "open_questions": [],
        "parsed_from": source,
        "parsed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    section: str | None = None
    current: dict | None = None
    desc: list[str] = []

    for raw in text.splitlines():
        line = raw.rstrip()

        m1 = H1.match(line)
        if m1 and ctx["context_name"] is None:
            ctx["context_name"] = m1.group(1).strip()
            section = None
            continue
        m2 = H2.match(line)
        if m2:
            section = m2.group(1).strip().lower()
            current = None
            continue
        m3 = H3.match(line)
        if m3:
            current = new_term(m3.group(1).strip())
            ctx["terms"].append(current)
            continue

        if section is None:
            if ctx["context_name"] and line.strip() and not line.lstrip().startswith(">"):
                desc.append(line.strip())
            continue

        key = section.split()[0] if section else ""

        if key == "scope":
            mf = BULLET_FIELD.match(line)
            if mf:
                k = mf.group(1).strip().lower()
                if k in ("in", "out"):
                    ctx["scope"][k] = split_list(mf.group(2).strip())
            continue

        if key == "language":
            if current is None:
                continue
            mf = BULLET_FIELD.match(line)
            if mf:
                field = mf.group(1).strip()
                val = mf.group(2).strip()
                fl = field.lower()
                if field in LIST_FIELDS:
                    if fl == "aliases":
                        current["aliases"] = split_list(val)
                    elif fl == "avoid":
                        current["avoid"] = split_list(val)
                    elif fl == "see also":
                        current["see_also"] = split_list(val)
                elif field in SCALAR_FIELDS:
                    current[SCALAR_KEY[fl]] = val
            elif line.strip() and not line.lstrip().startswith("<!--"):
                cur = line.strip()
                current["definition"] = (current["definition"] + " " + cur).strip() if current["definition"] else cur
            continue

        if key == "relationship":
            mb = BULLET_PLAIN.match(line)
            if mb and not mb.group(1).startswith("*"):
                ctx["relationships"].append(mb.group(1).strip())
            continue

        if key == "open" and "question" in section:
            mo = OQ.match(line)
            if mo:
                ctx["open_questions"].append({"text": mo.group(2).strip(), "status": mo.group(1).lower()})
            else:
                mb = BULLET_PLAIN.match(line)
                if mb and not mb.group(1).startswith("*"):
                    ctx["open_questions"].append({"text": mb.group(1).strip(), "status": "unresolved"})
            continue

    ctx["description"] = " ".join(desc).strip()
    return ctx


def normalize_name(name: str) -> str:
    # 去掉中文/英文括号注释，取主词：'Plan Tree（计划树）' → 'Plan Tree'
    return re.split(r"[（(]", name, maxsplit=1)[0].strip()


def validate_context(ctx: dict) -> list[str]:
    problems: list[str] = []
    if not ctx["context_name"]:
        problems.append("缺一级标题（context_name）")
    # 重复术语（按规范化主词判重）
    seen: set[str] = set()
    for t in ctx["terms"]:
        nk = normalize_name(t["name"])
        if nk in seen:
            problems.append(f"重复术语: {t['name']}")
        seen.add(nk)
    # 可匹配键：完整名 + 规范化主词（See also / Alias 据此匹配）
    term_keys: set[str] = set()
    for t in ctx["terms"]:
        term_keys.add(t["name"].strip())
        term_keys.add(normalize_name(t["name"]))
    for t in ctx["terms"]:
        if not t["definition"]:
            problems.append(f"术语缺定义: {t['name']}")
        if t["status"] and t["status"] not in VALID_STATUS:
            problems.append(f"Status 非法 ({t['status']}): {t['name']}，允许 {sorted(VALID_STATUS)}")
        for a in t["aliases"]:
            if a in term_keys:
                problems.append(f"Alias 与术语主词冲突: {a}（在 {t['name']}）")
        for ref in t["see_also"]:
            if ref not in term_keys:
                problems.append(f"悬空 See also: {ref}（在 {t['name']}）")
    return problems


def find_context_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("CONTEXT.md"))


def cmd_parse(args) -> int:
    p = Path(args.path)
    ctx = parse_context(p.read_text(encoding="utf-8"), str(p))
    out = json.dumps(ctx, ensure_ascii=False, indent=2)
    if args.o:
        Path(args.o).write_text(out, encoding="utf-8")
        print(f"已写入 {args.o}")
    else:
        print(out)
    return 0


def cmd_validate(args) -> int:
    target = Path(args.path)
    files = find_context_files(target)
    if not files:
        print(f"未找到 CONTEXT.md: {target}", file=sys.stderr)
        return 1
    total = 0
    fail = False
    for f in files:
        ctx = parse_context(f.read_text(encoding="utf-8"), str(f))
        problems = validate_context(ctx)
        total += len(ctx["terms"])
        if problems:
            fail = True
            print(f"\n✗ {f}（{len(ctx['terms'])} 术语）")
            for pr in problems:
                print(f"  - {pr}")
        else:
            print(f"✓ {f}（{len(ctx['terms'])} 术语，无问题）")
    print(f"\n共 {len(files)} 个 CONTEXT.md，{total} 个术语。")
    return 1 if fail else 0


def cmd_query(args) -> int:
    p = Path(args.path)
    ctx = parse_context(p.read_text(encoding="utf-8"), str(p))
    results = []
    for t in ctx["terms"]:
        if args.status:
            if t["status"] == args.status:
                results.append(t)
        elif args.keyword:
            kw = args.keyword.lower()
            hay = (t["name"] + " " + t["definition"] + " " + " ".join(t["aliases"])).lower()
            if kw in hay:
                results.append(t)
    if not results:
        print("无匹配术语。")
        return 0
    for t in results:
        print(f"\n● {t['name']}  [{t['status'] or '—'}]")
        if t["definition"]:
            print(f"  {t['definition']}")
        if t["aliases"]:
            print(f"  Aliases: {', '.join(t['aliases'])}")
        if t["see_also"]:
            print(f"  See also: {', '.join(t['see_also'])}")
    return 0


def cmd_generate_map(args) -> int:
    root = Path(args.root)
    files = [f for f in find_context_files(root) if f.parent != root]
    lines = [
        "# Context Map", "",
        "项目级共用术语见 [./CONTEXT.md](./CONTEXT.md)；下列为各限界上下文。", "",
        "## Contexts", "",
    ]
    for f in files:
        ctx = parse_context(f.read_text(encoding="utf-8"), str(f))
        rel = f.relative_to(root).as_posix()
        desc = (ctx["description"][:50] + "…") if len(ctx["description"]) > 50 else ctx["description"]
        name = ctx["context_name"] or f.parent.name
        lines.append(f"- [{name}]({rel}) — {desc}".rstrip())
    lines += ["", "## Relationships", "",
              "（各上下文间的关系：发布/消费事件、共享类型、集成模式。按需补充。）", ""]
    out = "\n".join(lines)
    if args.o:
        Path(args.o).write_text(out, encoding="utf-8")
        print(f"已写入 {args.o}")
    else:
        print(out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="管理 CONTEXT.md 限界上下文术语表")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("parse", help="解析 CONTEXT.md → JSON")
    pp.add_argument("path")
    pp.add_argument("-o", help="输出 JSON 文件路径")
    pp.set_defaults(func=cmd_parse)

    pv = sub.add_parser("validate", help="校验术语表")
    pv.add_argument("path", help="CONTEXT.md 文件或目录")
    pv.set_defaults(func=cmd_validate)

    pq = sub.add_parser("query", help="查询术语")
    pq.add_argument("path")
    pq.add_argument("keyword", nargs="?")
    pq.add_argument("--status", choices=sorted(VALID_STATUS))
    pq.set_defaults(func=cmd_query)

    pm = sub.add_parser("generate-map", help="多上下文：生成 CONTEXT-MAP.md")
    pm.add_argument("root")
    pm.add_argument("-o")
    pm.set_defaults(func=cmd_generate_map)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
