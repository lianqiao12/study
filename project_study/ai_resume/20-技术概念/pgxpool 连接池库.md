# pgxpool 连接池库

#概念/Go #概念/数据库

> `github.com/jackc/pgx/v5/pgxpool` —— Go 连 PostgreSQL 的**连接池**库。ai-resume 的 Go 后端用它访问 Postgres。

## 是什么
pgx 是 Postgres 的纯 Go 驱动;`pgxpool` 是它上面的连接池封装。启动时建一个 `*pgxpool.Pool`,内部维护多个到 DB 的真实连接,请求来时借、用完还(见 [[连接池 Connection Pool]])。

## 使用流程(来自本项目)

### 1. 建池(启动时,一次)
`apps/api/cmd/server/main.go:19`
```go
pool, err := pgxpool.New(context.Background(), cfg.DatabaseURL)
if err != nil {
    log.Fatal(err)
}
defer pool.Close()   // 程序退出时关池,释放连接
```
- 用 `context.Background()`(启动期,非请求 ctx,见 [[请求上下文是什么|请求上下文]])。
- 必须判 `err`(见 [[nil|Go 的 nil 与错误处理]]),连不上库就别硬跑。

### 2. 注入 repository(依赖注入)
`router.go:15` / `resume.go:18`
```go
func New(cfg config.Config, pool *pgxpool.Pool) *echo.Echo { ... }
func NewResumeRepo(pool *pgxpool.Pool) *ResumeRepo { return &ResumeRepo{Pool: pool} }
```
repository 结构体持有 `Pool *pgxpool.Pool`,在装配时从 `pool` 注入,而非内部自己建连。

### 3. 直接用池执行 SQL(无需手动 Acquire)
`resume.go` 里全是直接调池方法,池自动借还连接:
```go
err := r.Pool.QueryRow(ctx, `SELECT ... WHERE id=$1`, id)   // 单行查询
rows, err := r.Pool.Query(ctx, `SELECT ...`)                // 多行
_, err = r.Pool.Exec(ctx, `INSERT ...`, arg)                // 写操作
```
- `$1,$2` 是 pgx 占位符(不是 `?`)。
- `ctx` 是**请求上下文**:客户端断连时查询自动取消(见 [[请求上下文是什么|请求上下文]])。

## 常用方法
| 方法 | 用途 | 返回 |
|------|------|------|
| `pgxpool.New(ctx, connStr)` | 建池 | `(*Pool, error)` |
| `pool.QueryRow(ctx, sql, args...)` | 查单行 | `*Row`(`.Scan(&x)` 取值) |
| `pool.Query(ctx, sql, args...)` | 查多行 | `(Rows, error)`,需 `defer rows.Close()` |
| `pool.Exec(ctx, sql, args...)` | 增删改 | `(cmdTag, error)` |
| `pool.Begin(ctx)` | 开事务 | `(*Tx, error)` |
| `pool.Acquire(ctx)` | 手动借连接 | `(*Conn, error)`,记得 `defer conn.Release()` |
| `pool.Close()` | 关池 | — |

## 事务示例
```go
tx, err := pool.Begin(ctx)
if err != nil { return err }
defer tx.Rollback(ctx)        // 出错回滚;成功时下面 Commit 会使其无效
_, err = tx.Exec(ctx, `UPDATE ...`)
if err != nil { return err }
return tx.Commit(ctx)
```

## 易错点
- 忘了 `pool.Close()`(靠 `defer`)→ 连接泄漏。
- `pool.Query` 返回的 `rows` 必须 `defer rows.Close()`,否则连接不归还。
- 手动 `Acquire` 后忘了 `Release()` → 池耗尽(见 [[连接池 Connection Pool]])。
- SQL 用字符串拼接而非 `$1` 参数化 → SQL 注入风险。
- 建池用 `Background()`,请求内查询用请求的 `ctx`。

## 相关
- [[连接池 Connection Pool]] — pool 概念与本项目用法
- [[pgx 连接池与数据库迁移]] — 迁移 SQL 与 JSONB 表设计
- [[Go 后端分层架构]] — repository 层如何持有 pool
- [[请求上下文是什么|请求上下文]] — 为什么查询要带 ctx
- [[nil|Go 的 nil 与错误处理]] — `if err != nil` 判错
