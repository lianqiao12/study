# Go 作为网关代理 Python

#概念/Go #项目/ai-resume

> ai-resume 里 Go API 不当"执行者",而是"守门人":浏览器只连 Go,Go 反向代理到 Python agent,并把 Python 的 SSE 流透传给浏览器 + 落库。

## 模式(来自 `apps/api/internal/agent/gateway.go`)
```
Web ──POST /api/agents/:id/run──▶ Go Gateway ──POST /run──▶ Python
  ◀── SSE 事件流(透传) ──┘                          │
                                                    │ SSE
  └────────────────────────────────────────────────┘
        Gateway 同时把每条 Event 写入 agent_runs.events
```

## Run() 三件事
1. **开记录**:`uuid` 生成 `runID`,`ResumeRepo.CreateRun(...)` 建运行记录;取 resume 内容组装请求体。
2. **代理+透传**:`http.Post(AgentBaseURL+"/run", ...)`,拿到响应后把自己也变成 SSE 端点,逐行扫描上游 `data:` 行,`Flush()` 给浏览器。
3. **落库收尾**:边转发边收集 `model.Event`,流结束 `FinishRun(events, tokens, "done")` 写入 `agent_runs`。

## 设计要点
- **守门人**:agent 绝不直接连浏览器;错误(agent 不可达)由 Go 统一兜底为 `502 Bad Gateway`。
- **薄网关**:Go 不解析业务语义,只做字符串透传与持久化;协议语义在 `model.Event` + `docs/agent-protocol.md`(seam ④)。
- **token 估算**:按 `text` 事件 `delta` 长度 /4 粗算,用于审计/计费。

## 相关
- [[Go SSE 流式响应]] — 透传的底层实现
- [[ai-resume 项目架构]] — 整体数据流
- [[事件协议三端镜像]] — 透传的事件结构
