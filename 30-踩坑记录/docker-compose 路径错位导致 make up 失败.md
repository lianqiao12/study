# docker-compose 路径错位导致 make up 失败

#踩坑 #概念/容器

## 现象
`make up`(即 `docker compose -f infra/docker-compose.yml up -d --build`)起不来。api / web 服务报错,且 `make build` 阶段就可能失败。

## 根因
1. **路径基准错误**:compose 文件在 `infra/`,但 Makefile 从项目根调用。相对路径按 compose 文件目录解析,所以 `./apps/api` 变成 `infra/apps/api`(不存在),build context 找不到。
2. **文件内路径自相矛盾**:postgres 用 `./migrations`(相对 infra 正确 → `infra/migrations`),而 api 用 `./infra/migrations`(相对 infra 错误 → `infra/infra/migrations`)。
3. **源码挂载遮蔽产物**:即使 build 成功,`volumes: - ./apps/api:/app` 会把宿主机源码挂到容器 `/app`,盖掉镜像里编译好的 `/app/server` 二进制(api 的 `CMD` 直接跑它)→ `executable file not found`。web 同理,`.next` 被遮蔽 → `Could not find a production build`。

## 修复(方案 A:生产态)
- 统一路径为相对 `infra/`:build context 改 `../apps/api` 等,api 迁移挂载改 `./migrations`。
- 去掉 api / web 的源码挂载,用镜像内构建产物:
  ```yaml
  api:
    volumes:
      - ./migrations:/migrations:ro   # 删掉 - ./apps/api:/app
  web:
    volumes:
      - /app/node_modules             # 删掉 - ./apps/web:/app
  ```
- agent / postgres 不受影响(agent 跑源码、postgres 是独立镜像)。

## 教训
- 改 compose 后,先确认**调用方式(从哪、用什么 -f)**,再写相对路径。
- 见 [[Docker Compose 相对路径陷阱]]。

## 验证
本机无 Docker 时,可退而验证:路径文件是否存在 + YAML 合法(`python3 -c "import yaml; yaml.safe_load(...)"`)。
