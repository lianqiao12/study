# os.ReadDir 返回 DirEntry

#概念/Go

> `os.ReadDir(dir)` 返回 `[]os.DirEntry` —— 目录里每个文件/子目录对应一个 `DirEntry`,是**轻量列表项**(只有名字和类型,不含内容)。

## 用法
```go
entries, err := os.ReadDir(dir)   // entries 是 []os.DirEntry
for _, e := range entries {
    if e.IsDir() || !strings.HasSuffix(e.Name(), ".sql") { continue }
    b, _ := os.ReadFile(filepath.Join(dir, e.Name()))  // 要内容得另外读
}
```

## 单个 DirEntry 提供
| 方法 | 返回 | 说明 |
|------|------|------|
| `e.Name()` | 名字(不含路径) | `e.Name()` 取后缀判断 |
| `e.IsDir()` | 是否目录 bool | 跳过子目录 |
| `e.Type()` | 文件类型 | (常不直接用) |

## 关键点:只给名字不给内容
`DirEntry` 不含文件内容。要内容需另调 `os.ReadFile(filepath.Join(dir, e.Name()))`——这就是代码里拼路径再读的原因。

## 易混对比
- `os.ReadDir(dir)` → `[]DirEntry`(名字+类型,轻量)
- `os.ReadFile(path)` → `[]byte`(文件内容)
- `ioutil.ReadDir`(已弃用)曾返回 `[]FileInfo`

## 相关
- [[Go for range 遍历]] — 遍历 entries
- [[pgxpool 连接池库]] — runMigrations 用 ReadDir 找 .sql
- [[filepath Join 安全拼接路径]](待补) — 拼完整路径
