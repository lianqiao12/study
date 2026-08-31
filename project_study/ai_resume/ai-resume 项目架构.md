# ai-resume 项目架构

#项目/ai-resume

> 一个 AI 简历应用**脚手架**:核心数据是一份简历(jsonb 的 section 数组),agent 通过工具改简历并 SSE 流式推送,可导出 PDF/DOCX。重点是可扩展架构,而非写死的业务功能。

## 四服务结构

| 服务 | 技术 | 职责 |
|------|------|------|
| web | Next.js (React) | 数据驱动编辑器 + 实时预览 + SSE agent 控制台 |
| api | Go (Echo + pgx) | 唯一真相源:简历 CRUD、工具 API、导出、agent 网关 |
| agent | Python (FastAPI) | 产生 SSE 事件流的运行时,调 LLM 与工具 |
| postgres | 数据库 | resumes / agents / agent_runs / templates / users |

## 数据流

```
Web ──POST /api/agents/:id/run──▶ Go Gateway ──POST /run──▶ Python agent
  ◀── SSE 事件流 ──┘                                │
                                                    │ SSE 事件流
  └────────────────────────────────────────────────┘
         Python 改简历时回调 Go Tools API (bearer)
         Go 落库 (resume + agent_runs.events)
```

- 浏览器**只跟 Go API 说话**,绝不直接连 Python(守门人模式)。
- 详见 [[ai-resume 学习接手路线]]。

## 七条扩展缝(架构红线)

| 缝 | 落点 | 含义 |
|----|------|------|
| ① Runtime 注册表 | `agent/runtime/registry.py` | 新增 agent 类型不改 web/Go |
| ② 工具契约 | `api/handler/tools.go` ↔ `agent/tools/client.py` | 加工具只改 Go 一处 |
| ③ 外部状态存储 | `agent/runtime/checkpointer.py` | Python 无状态,状态可放 Redis |
| ④ 事件协议版本化 | `model/event.go` / `schemas/event.py` / `lib/event.ts` | 三端镜像同一份契约 |
| ⑤ 模型注册表 | `agent/runtime/model_registry.py` | 换 LLM 只注册 provider |
| ⑥ 数据驱动前端 | `apps/web/lib/types.ts` | 加区块类型只加模板行 |
| ⑦ 运行审计落库 | `api/agent/gateway.go` → `agent_runs` | 网关代理并审计每次运行 |

## 关键文件
- `apps/api/internal/agent/gateway.go` — SSE 代理 + 落库(见 [[SSE 流式通信]])
- `apps/agent/app/runtime/runtimes/builtin.py` — 内置 agent 完整可运行循环
- `apps/agent/app/agents/ats_optimizer.py` — `score()` 是占位,留给自己写
- `infra/docker-compose.yml` — 编排(曾踩坑,见 [[docker-compose 路径错位导致 make up 失败]])
