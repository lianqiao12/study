# Go 后端分层架构

#概念/Go #项目/ai-resume

> 以 ai-resume 的 `apps/api` 为例,看一个典型的 Go(clean-ish)后端分层。

## 分层

| 层 | 目录 | 职责 |
|----|------|------|
| 路由装配 | `internal/router` | 把所有 handler、gateway、中间件拼到 Echo 实例 |
| HTTP 层 | `internal/handler` | 解析请求、调 service、返回;不含业务 |
| 业务层 | `internal/service` | 跨实体的业务逻辑(如 section 变更) |
| 持久层 | `internal/repository` | 用 `pgxpool` 直接写 SQL,隔离数据库细节 |
| 模型 | `internal/model` | 数据结构 + 协议常量(如 `Event`) |
| 网关 | `internal/agent` | 代理外部运行时(见 [[Go 作为网关代理 Python]]) |

## 关键约定
- 依赖方向:handler → service → repository,单向,model 在最底层被各方引用。
- handler 通过**结构体字段注入依赖**(如 `ResumeHandler{Repo, Svc}`),在 `router.New()` 里 `NewXxx(...)` 组装,而非全局变量。
- 入口 `cmd/server/main.go`:自动迁移 + 启动 Echo。

## 与 Python 侧的边界
- Go 是"唯一真相源",所有简历写操作都经 Go 的 Tools API(seam ②),Python 无状态。
- 见 [[ai-resume 项目架构]]。

## 易错点
- repository 直接拼 SQL 易 SQL 注入 → 用参数化(`$1,$2`)而非字符串拼接。
- 跨层传递 `context.Context` 做超时/取消,不要存进结构体。
