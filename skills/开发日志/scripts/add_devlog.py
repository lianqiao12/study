#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向个人知识库的开发日志追加条目。

用法:
  python3 add_devlog.py "今天做了 XXX"
  python3 add_devlog.py --date 2026-09-01 "指定日期的条目"
  (echo 第一行 & echo 第二行) | python3 add_devlog.py
"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

# skills/开发日志/scripts -> 上溯 3 级到知识库根目录
ROOT = Path(__file__).resolve().parents[3]
TPL = """# 开发日志 {date}

> 每日记录开发进展。条目按时间倒序追加,最新在最上方。

"""


def build_entry(text: str, now: str):
    items = [ln.strip() for ln in text.splitlines() if ln.strip()]
    block = ["", f"## {now}", ""]
    block += [f"- {it}" for it in items]
    block.append("")
    return block


def main():
    ap = argparse.ArgumentParser(description="追加开发日志条目")
    ap.add_argument("entry", nargs="*", help="条目文本(省略则从 stdin 读取)")
    ap.add_argument("--date", default=date.today().strftime("%Y-%m-%d"),
                    help="日志日期 YYYY-MM-DD,默认今天")
    ap.add_argument("--root", default=str(ROOT), help="知识库根目录")
    args = ap.parse_args()

    root = Path(args.root)
    log_dir = root / "开发日志"
    log_dir.mkdir(parents=True, exist_ok=True)

    path = log_dir / f"{args.date}.md"
    text = " ".join(args.entry).strip() or sys.stdin.read().strip()
    if not text:
        print(f"[跳过] 无内容,未写入: {path}")
        return

    now = datetime.now().strftime("%H:%M")
    block = build_entry(text, now)

    if not path.exists():
        content = TPL.format(date=args.date)
        lines = content.split("\n")
    else:
        lines = path.read_text(encoding="utf-8").split("\n")

    # 最新在最上方:插到第一个 "## " 之前;若没有则追加到末尾
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("## "):
            insert_at = i
            break
    lines = lines[:insert_at] + block + lines[insert_at:]
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"[完成] 已写入 {path}  ({args.date} {now})")


if __name__ == "__main__":
    main()
