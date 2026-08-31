# ai-resume 学习接手路线

#学习 #项目/ai-resume

> 作为学习项目,骨架(管道)已通、血肉(智能)待填。建议按顺序接手,每步都能立刻看到效果。

## 当前真实状态
- ✅ 已通:数据库 schema、Go API 路由/仓库、Python `BuiltinRuntime` 完整循环、SSE 三端协议、PDF/DOCX 导出。
- 🔲 待写(你的活):
  1. `apps/agent/app/agents/ats_optimizer.py` 的 `score()` 是 keyword 占位,需换真实逻辑。
  2. `apps/agent/app/runtime/model_registry.py` 有 `NotImplementedError`,目前只有 `StubProvider`(返回假文本)。
  3. `grammar-polish` agent 几乎空,可照 `ats_optimizer` 写。
  4. 前端 `AgentPanel.tsx` 有 TODO,SSE 控制台可能未完全接好。
  5. checkpointer 是内存版,需持久化可实现 Redis/Postgres 版。

## 推荐顺序
1. **跑通基准线**:`make up` 确认整条管道流动(见 [[ai-resume 项目架构]])。
2. **填 `score()` / 加自己的 agent**:最小独立改动,只动 `apps/agent/app/agents/`。
3. **接真 LLM**:实现 `model_registry.py` 里一个 provider,把 `StubProvider` 换掉,agent 立刻变聪明。
4. **前端接 SSE**:补完 `AgentPanel.tsx` 的 TODO,让流式输出显示在网页。
5. 进阶:checkpointer 持久化、新 Runtime(mcp/webhook/openapi)。

## 起点文件
- 网关:SSE 代理 + 落库 → [[SSE 流式通信]]
- 内置循环:`apps/agent/app/runtime/runtimes/builtin.py`
- 占位点:`apps/agent/app/agents/ats_optimizer.py`
