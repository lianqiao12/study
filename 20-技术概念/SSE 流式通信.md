# SSE 流式通信

#概念/通信

> Server-Sent Events:基于 HTTP 的**单向**服务端→客户端流式推送,使用 `text/event-stream` 媒体类型。

## 协议要点
- 响应头必须设 `Content-Type: text/event-stream`、`Cache-Control: no-cache`、`Connection: keep-alive`。
- 每帧格式:`data: <json>\n\n`(两个换行分隔事件)。
- 服务端用 `Flush()` 即时把缓冲推给客户端,实现"打字机"效果。

## 在 ai-resume 中的用法
- Python `agent` 的 `/run` 端点用 `StreamingResponse` 逐条 `yield "data: {...}\n\n"`。
- Go `gateway.go` 收到后**逐行透传**给 Web,同时收集事件落库:
  ```go
  fmt.Fprintf(c.Response(), "data: %s\n\n", payload)
  c.Response().Flush()
  ```
- Web 端 `lib/api.ts` 的 SSE 运行器消费流。
- 协议契约见 [[事件协议三端镜像]]。

## 易错点
- `bufio.Scanner` 默认缓冲区 64KB,大事件(如整段 `section_patch`)会被截断 → 需 `scanner.Buffer(make([]byte,1024*1024), 8*1024*1024)`。
- SSE 是单向的;客户端若需回传指令,另走普通 HTTP 请求。
