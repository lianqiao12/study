# Docker Compose 相对路径陷阱

#概念/容器

> 关键规则:**`docker-compose.yml` 里的相对路径,是相对于 compose 文件自身所在目录解析的,而不是当前工作目录(CWD)。**

## 现象
- 文件在 `infra/docker-compose.yml`,但用 `docker compose -f infra/docker-compose.yml up`(从项目根目录调用)。
- 里面写 `build.context: ./apps/api` → 实际解析成 `infra/apps/api`(**不存在**)→ `make build` 直接失败。
- 同理 `volumes: ./apps/api:/app` 会把宿主机(错误路径创建的空目录)挂进容器,遮蔽镜像内产物。

## 判定方法
Docker Compose 的 project directory 默认 = compose 文件目录。可用 `--project-directory .` 强制改成 CWD,或把 compose 内路径写成相对文件目录的形式(如 `../apps/api`)。

## 自检
不确定路径怎么解析时,记住:**看 compose 文件放哪,相对路径就从哪算**。

相关踩坑:[[docker-compose 路径错位导致 make up 失败]]
