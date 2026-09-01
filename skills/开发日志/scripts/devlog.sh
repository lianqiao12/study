#!/usr/bin/env bash
# 在 WSL / Linux 下便捷记录开发日志到 Obsidian 知识库。路径自适应,可跨机使用。
# 用法:
#   devlog "今天做了什么"
#   echo -e "行1\n行2" | devlog
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$VAULT/skills/开发日志/scripts/add_devlog.py"
if [ ! -f "$SCRIPT" ]; then
  echo "找不到脚本: $SCRIPT" >&2
  exit 1
fi
exec python3 "$SCRIPT" --root "$VAULT" "$@"
