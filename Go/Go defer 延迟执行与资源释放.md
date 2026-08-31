# Go defer 延迟执行与资源释放

#概念/Go

> `defer` = 延迟执行:后面跟的函数调用,等**所在函数返回前**(正常 return 或 panic)才自动执行。是 Go 管理资源释放的惯用法。

## 基本
```go
pool, err := pgxpool.New(context.Background(), cfg.DatabaseURL)
if err != nil { log.Fatal(err) }
defer pool.Close()   // main 退出前才关池,不是现在关
```
含义:先记着,等外层函数结束时再调 `pool.Close()` 释放连接。

## 为什么用 defer
- **保证释放**:无论后面怎么 return / panic,defer 一定执行,不泄漏资源。
- **就近声明**:创建资源处立刻写销毁,不怕中间加 return 忘了关。
- **LIFO**:多个 defer 后进先出(栈序)。`defer a(); defer b()` -> 先 b 后 a。

## 常见搭配(凡是"开了资源"几乎都配 defer)
```go
rows, err := pool.Query(ctx, sql)
defer rows.Close()          // 结果集用完关,否则连接不归还

conn, err := pool.Acquire(ctx)
defer conn.Release()        // 手动借的连接用完必须还
```

## 坑
- `defer` 后的函数**参数在 defer 时即求值**,函数体延迟执行:
  ```go
  for i := 0; i < 3; i++ { defer fmt.Println(i) }  // 输出 3 3 3
  ```
  需捕获当时值要用闭包或新变量。

## 相关
- [[pgxpool 连接池库]] -- `defer pool.Close()` / `rows.Close()` 用法
- [[连接池 Connection Pool]] -- 不释放会池耗尽
