# Go SSE 流式响应

#概念/Go #概念/通信

> 在 Go(Echo)里手动实现 Server-Sent Events 流式响应。关键在 `Flush()` 与缓冲区大小。

## 核心代码(来自 gateway.go)
```go
c.Response().Header().Set("Content-Type", "text/event-stream")
c.Response().Header().Set("Cache-Control", "no-cache")
c.Response().Header().Set("Connection", "keep-alive")
c.Response().WriteHeader(http.StatusOK)

scanner := bufio.NewScanner(resp.Body)
scanner.Buffer(make([]byte, 1024*1024), 8*1024*1024) // 关键:放大缓冲
for scanner.Scan() {
    line := scanner.Text()
    fmt.Fprintf(c.Response(), "data: %s\n\n", payload)
    c.Response().Flush()   // 逐帧推给客户端
}
```

## 为什么必须放大缓冲区
`bufio.Scanner` 默认最大 token 64KB。一帧 SSE 事件(如整段 `section_patch` 的 JSON)可能远超 64KB,默认缓冲会直接 `bufio.Scanner: token too long` 截断流。因此:
```go
scanner.Buffer(make([]byte, 1024*1024), 8*1024*1024) // 初始 1MB,上限 8MB
```

## 要点
- SSE 用 `text/event-stream`,每帧 `data: <json>\n\n`。
- 必须 `Flush()` 才真正推到客户端,否则会等缓冲满才发(失去"打字机"效果)。
- 上游(这里 Python)也是 SSE,Go 在这里扮演**透传代理**:读上游流、原样写下游流。

## 相关
- [[SSE 流式通信]] — SSE 协议总览
- [[Go 作为网关代理 Python]] — 这段代码的上下文
- [[事件协议三端镜像]] — data 里的 JSON 结构
