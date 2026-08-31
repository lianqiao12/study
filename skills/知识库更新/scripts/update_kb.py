#!/usr/bin/env python3
"""重建 Obsidian 知识库首页索引。

扫描知识库根目录下的分类子目录(形如 NN-名称/),收集其中的 .md 笔记,
生成 / 更新 `00-索引/首页.md` 的索引区块。用法:

    python3 update_kb.py --root /mnt/c/develop/obsidian/doc/zzz

只对 00-索引/首页.md 中由标记行包围的索引区块做原地替换,保留文件其余内容,
因此首页顶部的人工说明不会丢失。
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

INDEX_START = "<!-- INDEX_START -->"
INDEX_END = "<!-- INDEX_END -->"


def collect_notes(root: Path) -> dict[str, list[str]]:
    """返回 {分类标题: [笔记名, ...]},按目录名排序。"""
    cats: dict[str, list[str]] = {}
    for d in sorted(p for p in root.iterdir() if p.is_dir() and re.match(r"^\d+-", p.name)):
        if d.name.startswith("00-"):
            continue  # 索引目录自身
        notes = []
        for md in sorted(d.glob("*.md")):
            if md.name == "欢迎.md":
                continue
            notes.append(md.stem)
        if notes:
            cats[d.name] = notes
    return cats


def render_index(cats: dict[str, list[str]]) -> str:
    lines = ["## 索引", ""]
    for cat, notes in cats.items():
        lines.append(f"### {cat}")
        for n in notes:
            lines.append(f"- [[{n}]]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_home(root: Path) -> None:
    home = root / "00-索引" / "首页.md"
    if not home.exists():
        home.parent.mkdir(parents=True, exist_ok=True)
        home.write_text(f"{INDEX_START}\n{INDEX_END}\n", encoding="utf-8")

    cats = collect_notes(root)
    block = f"{INDEX_START}\n{render_index(cats)}{INDEX_END}"

    text = home.read_text(encoding="utf-8")
    if INDEX_START in text and INDEX_END in text:
        new_text = re.sub(
            re.escape(INDEX_START) + r".*?" + re.escape(INDEX_END),
            block,
            text,
            flags=re.DOTALL,
        )
        if new_text == text:
            # 区块存在但内容相同,无需改写
            print("首页索引已是最新,无需更新。")
            return
        home.write_text(new_text, encoding="utf-8")
    else:
        home.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")

    print(f"已更新首页索引,收录 {sum(len(v) for v in cats.values())} 篇笔记,分 {len(cats)} 类。")


def main() -> None:
    ap = argparse.ArgumentParser(description="重建 Obsidian 知识库首页索引")
    ap.add_argument("--root", required=True, help="知识库根目录(含 00-索引/ 等)")
    args = ap.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"根目录不存在: {root}")
    update_home(root)


if __name__ == "__main__":
    main()
