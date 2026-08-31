# pgx 连接池与数据库迁移

#概念/Go #概念/数据库

> ai-resume 的 Go 后端用 `github.com/jackc/pgx/v5/pgxpool` 直连 Postgres,迁移 SQL 放在 `infra/migrations/`。

## 连接池
- 启动时 `pgxpool.New(ctx, databaseURL)` 建一个全局 `*pgxpool.Pool`。
- repository 接收 pool(或从中 `Acquire()` 连接),而非每次 `sql.Open`。
- `DATABASE_URL` 形如 `postgres://user:pass@host:5432/db?sslmode=disable`。

## 迁移策略
- 迁移文件:`infra/migrations/0001_init.sql`,手工写 `CREATE TABLE IF NOT EXISTS` + 种子数据。
- 两种执行方式:
  - 启动自动:`cmd/server/main.go` 里跑一次迁移(项目实际做法,见代码)。
  - 手动:`make migrate` → `docker compose exec postgres psql -U resume -d resume -f /migrations/0001_init.sql`(挂载路径见 [[docker-compose 路径错位导致 make up 失败]])。
- 用 `CREATE TABLE IF NOT EXISTS` + `ON CONFLICT DO NOTHING` 保证幂等,可重复执行。

## 表设计要点(本项目)
- `resumes.content` 是 `JSONB` 的 section 数组 → 加新区块类型**无需迁移**,只需加模板行(seam ⑥)。
- `agent_runs.events` 是 `JSONB`,整段 SSE 事件数组落库,用于重放/审计。

## 易错点
- pgx 占位符是 `$1,$2`(不是 `?`)。
- 连接池忘了 `defer conn.Release()` 会耗尽连接。
- 迁移 SQL 与代码 model 不一致时,运行时才爆,建议 model 与迁移同评审。

## 相关
- [[Go 后端分层架构]] — repository 层怎么用 pool
- [[ai-resume 项目架构]] — 表清单
