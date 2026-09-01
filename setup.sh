#!/usr/bin/env bash
# 新设备 clone 本仓库后,一键启用"开发日志"的 git 钩子。
# 用法(在仓库内任意位置执行): bash setup.sh
set -euo pipefail

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "错误:请在 git 仓库内运行 setup.sh" >&2; exit 1; }
HOOKS_DIR="$REPO/skills/开发日志/scripts/git-hooks"

if [ ! -d "$HOOKS_DIR" ]; then
  echo "错误:找不到钩子目录 $HOOKS_DIR" >&2
  exit 1
fi

# 1) 让 git 使用仓库内自带的钩子目录(绝对路径,跨机自适应)
git config core.hooksPath "$HOOKS_DIR"
echo "[ok] core.hooksPath = $HOOKS_DIR"

# 2) 赋予可执行权限(WSL/Linux 必须;Windows/Git-Bash 下忽略错误)
chmod +x "$HOOKS_DIR"/* 2>/dev/null || true
echo "[ok] 已对钩子加可执行位(Windows 可忽略)"

# 3) 检查 Python 是否可用(钩子依赖它写开发日志)
if command -v python3 >/dev/null 2>&1; then
  echo "[ok] 检测到 python3"
elif command -v python >/dev/null 2>&1; then
  echo "[ok] 检测到 python"
else
  echo "[警告] 未检测到 Python,钩子不会写入开发日志,请先安装 Python" >&2
fi

echo ""
echo "完成。此后 git commit / git push 会自动写开发日志(开发日志/YYYY-MM-DD.md)。"
