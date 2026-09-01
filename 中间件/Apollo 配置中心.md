# Apollo 配置中心

> 携程开源的**分布式配置中心**。统一管理微服务配置,支持热发布、灰度发布、版本回滚、权限隔离与多环境隔离。
> 典型场景:把数据库地址、开关、限流阈值等从代码/包里抽出来,运行时动态下发,改配置不用重新发版。

#概念/中间件

> [!tip] 速记卡（速查）
> | 维度 | 要点 |
> |------|------|
> | 是什么 | 携程开源分布式配置中心;热发布 / 灰度 / 回滚 / 多环境 |
> | 核心组件 | Config(读+推·8080) · Admin(写·8090) · Portal(界面·8070) · Meta+Eureka(发现) · Client(缓存) |
> | 四层模型 | 环境 → 集群 → AppId → Namespace |
> | 寻址 | `环境 + 集群 + AppId + Namespace` 唯一确定一份配置 |
> | 配置获取 | HTTP 长轮询 + 三级缓存(内存 → 文件 → classpath) |
> | 配置发布 | Portal → Admin → DB → 5s 轮询扫描兜底(最终一致) |
> | 灰度 | 按 Client IP 匹配,小流量 → 全量 / 回滚 |
> | 部署 | PortalDB(共享) + ConfigDB(每环境);config/admin 无状态可扩 |
> | 横向对比 | Nacos(配置+注册合一) / SCC·etcd(配置能力弱) |

## 目录

- [一、定位与对比](#一定位与对比)
- [二、整体架构](#二整体架构核心组件)
- [三、核心概念(四层模型)](#三核心概念四层模型)
- [四、配置获取流程](#四配置获取流程client-侧)
- [五、配置发布流程](#五配置发布流程)
- [六、灰度发布](#六灰度发布gray-release)
- [七、权限与审计](#七权限与审计)
- [八、客户端接入](#八客户端接入)
- [九、部署要点](#九部署要点)
- [十、高可用与一致性](#十高可用与一致性)
- [十一、常见坑](#十一常见坑)

---

## 一、定位与对比

为什么不用配置文件 / 环境变量:

- 配置散落在各服务、各机器,改一处要全量发版;
- 缺乏审计、权限、灰度,改错只能回滚代码;
- 无法按环境/集群/机器差异化下发。

同类中间件对比:

| 组件 | 厂商 | 配置能力 | 注册发现 | 灰度/权限/UI | 备注 |
|------|------|---------|---------|-------------|------|
| **Apollo** | 携程 | 强 | 自带(Eureka) | 强(Portal 完善) | 企业级配置首选 |
| **Nacos** | 阿里 | 强 | 强(合一) | 中 | 配置+注册合一,生态好 |
| Spring Cloud Config | Pivotal | 弱 | 无(配 Eureka) | 弱 | 简单,缺 UI/灰度 |
| etcd / Consul | — | 弱 | 强 | 弱 | 偏 KV/服务发现 |

Apollo 的核心卖点:**完善的 Portal UI + 灰度 + 权限 + 审计 + 多环境**,适合中大型微服务体系。

---

## 二、整体架构(核心组件)

```
                ┌─────────────┐
   浏览器 ─────▶ │   Portal    │ 管理界面(8070),不绑定具体环境
                └──────┬──────┘
                       │ 通过 Meta Server 发现各环境 Admin Service
            ┌──────────┼──────────────────────────┐
            ▼          ▼                            ▼
      [环境 DEV]   [环境 FAT]                 [环境 UAT]   (物理隔离)
   ┌──────────┐  ┌──────────┐              ┌──────────┐
   │ Admin    │  │ Admin    │              │ Admin    │  管理接口,写 DB
   │ Service  │  │ Service  │              │ Service  │
   └────┬─────┘  └────┬─────┘              └────┬─────┘
        │ 写配置       │                           │
   ┌────▼─────┐  ┌────▼─────┐              ┌────▼─────┐
   │ Config   │  │ Config   │              │ Config   │  读接口 + 推送(长轮询)
   │ Service  │  │ Service  │              │ Service  │  内嵌 Eureka(Meta Server)
   └────┬─────┘  └────┬─────┘              └────┬─────┘
        │ 注册          │                           │
   ┌────▼──────────────▼──────────────────────────▼─────┐
   │                  Eureka 注册中心                     │
   └─────────────────────────────────────────────────────┘
        ▲ 长轮询 /configs、/notifications
        │
   ┌────┴─────┐
   │  Client  │  应用内 SDK:内存 + 本地文件缓存兜底
   └──────────┘
```

- **Config Service**:向 Client 提供配置读取与变更推送(基于 HTTP 长轮询);每个环境部署一套;内嵌 Eureka,承担 Meta Server 角色。端口默认 `8080`。
- **Admin Service**:向 Portal 提供配置管理(修改/发布)接口;把变更写入 DB 并发通知;每个环境一套。端口默认 `8090`。
- **Portal**:统一管理界面,跨环境操作;通过 Meta Server 发现各环境 Admin Service;独立部署,不随环境变化。端口默认 `8070`。
- **Client**:应用端 SDK,从 Config Service 拉取配置、监听变更;本地多级缓存。
- **Meta Server**:基于 Eureka 封装的服务发现,给 Portal/Client 返回 Admin/Config Service 地址。与 Config Service 同进程(8080,路径 `/services/...`)。
- **Eureka**:服务注册发现。Config/Admin Service 启动时注册到 Eureka,Meta Server 从中取实例列表。

---

## 三、核心概念(四层模型)

配置的组织维度,从上到下:

1. **Environment 环境**:`DEV / FAT / UAT / PRO`(也可自定义)。**物理隔离**,不同环境网络不通、连不同 DB。由 Client 的 `env` 决定连哪套。
2. **Cluster 集群**:同一环境内再分组(如不同机房/可用区),默认集群 `default`。用于同一环境内差异化配置。
3. **AppId 应用**:应用唯一标识(`app.id`)。Client 用它在某环境下定位自己的配置。
4. **Namespace 命名空间**:配置分组,分两类:
   - **私有 Namespace**:应用自己独享(默认 `application`)。
   - **公共 Namespace**:多个应用共享(如统一的 DB、Redis 配置),其他应用可**关联**后继承并覆盖其中部分 key。
   - 文件类型:`properties`(默认)、`xml`、`json`、`yml/yaml`、`text`。
5. **Item 配置项**:`key = value` + 注释 + 类型(默认/String/Number/Boolean)。

寻址公式:`环境 + 集群 + AppId + Namespace` 唯一确定一份配置。

---

## 四、配置获取流程(Client 侧)

启动时:

1. Client 读 `app.id`、`apollo.meta`(Meta Server 地址)、`env`;
2. 向 Meta Server 拿到 Config Service 实例列表,选一个;
3. 发起**长轮询** `GET /notifications/v2?appId=&cluster=&notifications=...`(默认超时 ~60s);
4. 配置未变则长轮询挂起,变更时服务端立即返回 `notificationId` 变化;
5. Client 再拉 `GET /configs/{appId}/{cluster}/{namespace}` 全量配置,写入内存;
6. 同时落本地缓存文件。

**本地缓存(兜底)**,优先级由高到低:

- 内存(运行时)
- 文件:`${apollo.cacheDir}`(默认 Linux `/opt/data/{appId}/config-cache/`,Windows `C:\opt\data\{appId}\config-cache/`)下的 `.properties`
- classpath 下 `config/` 目录的默认配置(打包时内置)

> 关键价值:即使 Config Service 全挂,应用也能用**上次缓存的文件**正常启动,不会因配置中心不可用而雪崩。

---

## 五、配置发布流程

1. 用户在 Portal 修改某个 Item → Portal 调对应环境 Admin Service;
2. Admin Service 把配置写入 DB(`ApolloConfigDB` 的 `ReleaseMessage` 表记录一条发布消息),并标记新版本;
3. Config Service 内有定时线程(默认每 **5s**)扫描 `ReleaseMessage`,发现新发布 → 通知对应客户端;
4. Client 长轮询被唤醒 → 拉取全量新配置 → 更新内存与本地缓存 → 触发 `@ApolloConfigChangeListener`。

> **最终一致性保证**:即使通知在中间环节丢失,Config Service 的 5s 轮询扫描也能兜底,最多 5s 内所有客户端感知到变更。

---

## 六、灰度发布(Gray Release)

针对**同一环境内的特定实例**先放一部分,验证无误再全量:

- 灰度维度:按 **Client IP 列表**(或 label)匹配;
- 流程:在 Namespace 上建灰度 → 指定灰度机器 IP → 发布灰度版本 → 观察 → 全量发布 / 回滚;
- 适用:开关上线、参数调优、风险变更先小流量验证。

---

## 七、权限与审计

- **项目级 + Namespace 级**权限:查看 / 修改 / 发布 / 授权 四种动作可分别授予不同角色;
- **发布历史**:每次发布记录操作人、时间、变更 diff,可一键回滚到任意历史版本;
- 适合有合规/审计要求的团队。

---

## 八、客户端接入

### Java(Spring Boot)

```xml
<dependency>
  <groupId>com.ctrip.framework.apollo</groupId>
  <artifactId>apollo-client</artifactId>
  <version>2.x</version>
</dependency>
```

```java
@EnableApolloConfig                       // 启用 Apollo 配置
@Component
public class Demo {
    @Value("${switch.feature.x:false}")   // 直接注入
    private boolean featureX;

    @ApolloConfigChangeListener("application")
    public void onChange(ConfigChangeEvent e) {
        if (e.isChanged("switch.feature.x")) { /* 热更新后处理 */ }
    }
}
```

关键配置(`app.properties` 或 JVM 参数):

- `-Dapp.id=order-service`
- `-Dapollo.meta=http://config-service:8080`
- `-Denv=DEV`(或 `server.properties` / 操作系统环境变量 `ENV`)

### Go

官方没有一等公民 Go SDK,常用社区客户端(如 `agollo` 系),本质也是拉取 + 长轮询 + 本地缓存:

```go
// 伪代码:agollo 风格
agollo.Init("http://config-service:8080", "order-service",
    agollo.WithNamespace("application"),
    agollo.WithEnv("DEV"))
val := agollo.GetString("switch.feature.x", "false")
agollo.OnChange(func(ns string, changes map[string]agollo.Change) { /* 热更新 */ })
```

> 选 Go 客户端时注意:社区库成熟度、是否支持灰度/公共 Namespace/本地缓存,按需评估。

---

## 九、部署要点

- **依赖 MySQL**:两个库
  - `ApolloPortalDB`:全局一份,存 Portal 元数据、项目/Namespace 定义(跨环境共享);
  - `ApolloConfigDB`:存各环境实际配置,**推荐每个环境独立一套**(物理隔离)。
- **组件清单**:`apollo-configservice`(含 Eureka/Meta Server)、`apollo-adminservice`、`apollo-portal`(可选 `apollo-bootstrap` 仅首次导入 Eureka)。
- **端口**:config `8080` / admin `8090` / portal `8070`。
- **多环境**:通常**每环境一套 config+admin**(连各自的 ApolloConfigDB),**共用一个 Portal**;Portal 通过 `apollo.portal.envs=dev,fat,uat` 与 `apollo.meta` 寻址。
- 生产建议:Config/Admin 无状态,可水平扩容;Eureka 多节点保证注册高可用。

---

## 十、高可用与一致性

- Client **本地文件缓存兜底**,Config Service 宕机不影响已运行应用启动;
- Config Service **无状态、可水平扩展**;
- 发布走 **DB + 5s 轮询扫描**,保证变更最终一致(不依赖消息队列也不丢);
- 多环境物理隔离,互不影响。

---

## 十一、常见坑

- `apollo.meta` 配成 Portal 地址(8070)→ 应配 **Config Service(8080)**;Meta Server 与 Config Service 同进程。
- `app.id` 与 Portal 里建的项目 AppId 不一致 → 拉不到配置。
- `env` 没设对 → 连错环境的 Config Service(尤其容器/K8s 里 ENV 变量被覆盖)。
- 长轮询被**反向代理/网关**截断(超时 < 60s)→ 配置不实时;需放行长连接或调小客户端长轮询超时。
- **公共 Namespace 改一处影响多个应用** → 公共配置变更要走评审/灰度,谨慎操作。
- `yml/yaml` 与 `properties` 解析差异 → 注意缩进与类型;默认 `properties` 最稳。
- 本地缓存目录权限不足(`/opt/data` 不可写)→ 兜底失效,注意挂载与权限。

---

相关:[[SSE 流式通信]](同为服务端→客户端实时通道思路,可对照长轮询)、[[Docker Compose 相对路径陷阱]](Apollo 容器化部署注意挂载 `/opt/data` 缓存目录)

思维导图:[[Apollo 配置中心 思维导图]]
