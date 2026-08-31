# Go 指针与值类型:为何返回 `*Pool`

#概念/Go

> Go 函数返回类型前的 `*` 表示**指针**(指向该类型对象的内存地址),而非值本身。

## 为什么 pgxpool.New 返回 `*pgxpool.Pool` 而不是 `pgxpool.Pool`
1. **共享同一份状态**:Pool 内部有连接、锁、计数器,是有状态大对象。返回指针 → 所有调用方拿的是**同一个对象地址**,共享同一池连接;`defer pool.Close()` 一关全关。
   - 若返回值类型:每次传递都**深拷贝**,repo1/repo2 各持一份独立池 → 连接数翻倍、关不掉原池 → 泄漏。
2. **避免大对象拷贝**:指针只传 8 字节地址,比拷贝整个结构体省内存/CPU。
3. **惯例**:需要被多处共享或修改内部状态的类型用指针(`*Pool`、`*bytes.Buffer`、`*os.File`);无共享状态的小类型用值。

## 本项目印证
```go
pool, _ := pgxpool.New(...)            // pool 是指针
resumeRepo := NewResumeRepo(pool)      // NewResumeRepo(pool *pgxpool.Pool) 收指针
```
各 repository 共享同一个池。

## 类比
`*Pool` 像健身房**卡号**:大家刷同一张卡号进同一个馆;值类型像每人复印一张卡,但复印卡开的是各自独立的馆,会员系统全乱。

## 相关
- [[pgxpool 连接池库]] — `New` 返回 `*Pool`,repo 共享
- [[nil|Go 的 nil 与错误处理]] — 指针的零值是 nil
