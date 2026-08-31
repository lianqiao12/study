# Echo 框架路由装配

#概念/Go

> Echo 是 Go 的轻量 HTTP 框架。ai-resume 的 `apps/api/internal/router/router.go` 展示了典型的装配模式。

## 装配模式
```go
func New(cfg config.Config, pool *pgxpool.Pool) *echo.Echo {
    e := echo.New()
    resumeRepo := repository.NewResumeRepo(pool)
    // ... 其它 repo / svc / handler
    gw := agent.NewGateway(cfg.AgentBaseURL, resumeRepo)

    e.GET("/health", health)
    e.GET("/api/resumes", resumeH.List)
    e.POST("/api/agents/:id/run", gw.Run)   // 网关挂在路由上
    return e
}
```

## 要点
- 一个 `echo.Echo` 实例 = 整个 HTTP 服务;路由用 `e.GET/POST(...)` 注册。
- handler 是普通函数 `func(c echo.Context) error`,从 `c.Param/Query/Bind` 取输入,`c.JSON/c.Response()` 输出。
- 路径参数 `:id` 用 `c.Param("id")` 取;SSE 场景直接用 `c.Response()` 写流(见 [[Go SSE 流式响应]])。
- 中间件/分组:`e.Group("/api/tools", authMW)` 给一组路由加鉴权(seam ②)。

## 启动
`cmd/server/main.go` 里 `e.Logger.Fatal(e.Start(":8080"))` 或读 `PORT` 环境变量。

## 相关
- [[Go 后端分层架构]] — handler/service/repository 怎么分工
- [[Go 作为网关代理 Python]] — `gw.Run` 这个 handler 干了什么
