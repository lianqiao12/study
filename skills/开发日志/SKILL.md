---
name: 开发日志
description: 此技能用于记录用户每天开发了什么,按日期写入本地 Obsidian 知识库的开发日志。当用户说"开发日志""记一下开发""今天开发了什么""记录开发""dev log""写开发日志",或想把当天/某天的开发进展(功能、修复、调试过程)沉淀成每日笔记时,应使用此技能。
---

# 开发日志

把每天的开发进展沉淀为按日期组织的笔记,落在知识库根目录的 `开发日志/`,
文件名 `YYYY-MM-DD.md`,一天一个文件。由 `scripts/add_devlog.py` 确定性地
创建与追加,无需手动建文件。

## 何时使用

- 用户说"开发日志 / 记一下开发 / 今天开发了什么 / 记录开发 / dev log"。
- 对话中出现当天完成的功能、修复、调试过程,且用户想保存为开发记录。
- 不要在闲聊中随意触发;用户明确要记,或内容明显是"开发产出"时启用。

## 日志结构

```
开发日志/
├── 2026-09-01.md   # 当天的开发记录(最新条目在最上方)
├── 2026-09-02.md
└── ...
```

单文件格式见 `references/format.md`。

## 执行流程

1. **确认内容**。若用户没说具体开发了什么,先问一句:"今天开发了什么?" 或
   从对话里提取可记录的产出(功能 / 修复 / 踩坑)。
2. **落盘条目**。调用脚本写入今天(或 `--date` 指定日期)的条目:
   ```bash
   # 单行
   python3 scripts/add_devlog.py "把仓库切到 SSH;给图谱配色"

   # 多行(每条一行)
   (echo 修复了登录超时 & echo 增加了开发日志 skill) | python3 scripts/add_devlog.py

   # 指定日期
   python3 scripts/add_devlog.py --date 2026-09-01 "整理知识库结构"
   ```
   脚本会自动建 `开发日志/YYYY-MM-DD.md`(含模板),并把新条目插到最上方。

   **兜底**:若环境里 `python3`/`py` 都不可用(报 "Python was not found"),
   则按 `references/format.md` 直接用文件写入创建/追加
   `开发日志/YYYY-MM-DD.md`,无需执行脚本。
3. **回执**。告诉用户写到了哪个文件、几条条目,提示可在 Obsidian 打开查看。
4. **(可选)提交**。若用户希望备份,顺手提交(本仓库用 SSH,联网正常时再推):
   ```bash
   git -C "c:/Users/Hame/Documents/ObsidianVault" add 开发日志 && git commit -m "devlog: 更新开发日志"
   ```

## 在 WSL / Linux 中触发

本机代码若在 WSL 中运行,仓库通过 `/mnt/c/...` 挂载,可直接调用脚本。
脚本会依据自身位置自动定位知识库根目录,无需额外配置:

```bash
python3 /mnt/c/Users/Hame/Documents/ObsidianVault/skills/开发日志/scripts/add_devlog.py "修复了 WSL 下的路径问题"
# 脚本在别处时,用 --root 显式指定根目录:
python3 add_devlog.py --root /mnt/c/Users/Hame/Documents/ObsidianVault "内容"
```

为方便,在 `~/.bashrc` / `~/.zshrc` 加个别名:

```bash
devlog() { python3 /mnt/c/Users/Hame/Documents/ObsidianVault/skills/开发日志/scripts/add_devlog.py --root /mnt/c/Users/Hame/Documents/ObsidianVault "$*"; }
```

之后在 WSL 任意目录直接 `devlog "今天做了什么"`。也可用仓库自带包装脚本
`scripts/devlog.sh`(内部已写好根目录):`bash devlog.sh "内容"`。

> `/mnt/c/Users/Hame/Documents/ObsidianVault` 与 Windows 侧
> `C:\Users\Hame\Documents\ObsidianVault` 是同一份文件,Obsidian 打开后立即可见。

## 与 git 提交联动(自动触发)

不想每次手动记,可让 `git commit` 自动写开发日志:用一个 `post-commit` 钩子
调用同一个 `add_devlog.py`,把提交信息作为条目写进当天日志。git 钩子无法直接
拉起 CodeBuddy 对话,但跑的是同一底层脚本,效果等价。

启用方式(二选一):

1. **直接用仓库内已放好的钩子**(本仓库 `.git/hooks/post-commit` 已就位):
   - WSL 下补可执行位:`chmod +x .git/hooks/post-commit`
   - Windows(Git for Windows)无需额外操作,提交即生效
2. **用 tracked 副本(便于克隆后复用)**:
   ```bash
   git config core.hooksPath skills/开发日志/scripts/git-hooks
   ```
   钩子文件见 `scripts/git-hooks/post-commit`。

行为说明:
- 钩子自动定位仓库根(`git rev-parse --show-toplevel`),Windows/WSL 路径都通用。
- 提交信息(标题+正文)按行拆成子弹写入 `开发日志/YYYY-MM-DD.md`,最新置顶。
- 合并/变基产生的提交默认跳过,避免刷屏。
- 写入的开发日志文件会变为未提交改动,记得择机 `git add 开发日志 && git commit`
  (或让它随下次提交一起进库)。
- 若环境无 python,钩子静默跳过,**不影响本次提交**。

### 上传(push)时也记录

`post-commit` 只在提交时触发;若想在 `git push`(上传)时也写一条,加
`pre-push` 钩子(见 `scripts/git-hooks/pre-push`):它会记录
"推送 N 个提交到 origin/main"。git 没有 `post-push`,故用推送前触发。

> **WSL 关键提醒**:在 WSL 里钩子文件必须有可执行位,否则 git 直接忽略。
> 一次性执行:
> ```bash
> chmod +x .git/hooks/post-commit .git/hooks/pre-push
> ```
> Windows(Git for Windows)不需要这步。若用了 `core.hooksPath` 指向 tracked 副本,
> 同样需要对那些文件 `chmod +x`。

## 写作约定

- 一条目 = 一个时间点(`## HH:MM`)+ 若干 `- 要点` 子弹。
- 每条一句话,动词开头,聚焦"做了什么 / 结果"。
- 踩坑类写"现象 → 根因 → 修复"三短句。
- 用 `[[双链]]` 关联相关笔记(如 `[[知识库更新]]`),便于图谱串联。

## 资源

- `scripts/add_devlog.py` — 按日期创建/追加开发日志的确定性脚本。
- `references/format.md` — 开发日志文件格式说明。
