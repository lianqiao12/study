# Go for range 遍历

#概念/Go

> `for ... range` 是 Go 遍历切片/数组/map/字符串/channel 的语法。

## 基本(切片/数组)
```go
for _, e := range entries {
    // 每次循环 e = entries 里的下一个元素
}
```
| 部分 | 含义 |
|------|------|
| `for` | 循环关键字 |
| `_` | 第一个返回值=**下标**(从0),用 `_` 表示"忽略" |
| `e` | 第二个返回值=**当前元素** |
| `range entries` | 要遍历的对象 |

等价传统写法:
```go
for i := 0; i < len(entries); i++ { e := entries[i]; ... }
```

## 为什么下标用 `_`
Go 编译器规定**声明了却不用的变量会报错**。`_` 是空标识符,表示"丢弃这个位置的值"。
- `for _, e := range` 忽略下标、保留元素
- `for i, _ := range` 保留下标、忽略元素

## range 对不同类型的返回值
| 对象 | 第一个值 | 第二个值 |
|------|----------|----------|
| 切片/数组 | 下标 int | 元素 |
| map | key | value |
| 字符串 | 下标 | 字符(rune) |
| channel | — | 取出的每个值(单返回值) |

## 在 runMigrations 里
```go
for _, e := range entries {
    if e.IsDir() || !strings.HasSuffix(e.Name(), ".sql") { continue }
    // e 是 os.DirEntry,依次检查/读/执行
}
```

## 坑
- 老版本 Go 中 `for _, e := range` 用 `&e` 取地址会拿到"同一循环变量地址";只读 `e.Name()` 不受影响。
- `range` 遍历 slice 时 `e` 是元素拷贝(值类型而言)。

## 相关
- [[pgxpool 连接池库]] — runMigrations 里遍历迁移文件
- [[os ReadDir 返回 DirEntry]] — entries 的类型
