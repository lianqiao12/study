# 单点登录 SSO 知识点

> 标签：#认证/SSO #单点登录 #IdP #OIDC #SAML #CAS

## 1. 什么是单点登录（SSO）

**SSO（Single Sign-On，单点登录）**：用户在一个系统中登录后，可以**无需再次登录**地访问其他相互信任的系统。

一句话：一次登录，处处通行。

核心解决的问题是：**企业内部/平台内存在多个子系统时，用户不必为每个系统重复输入账号密码**。

```text
没有 SSO：
  系统A 登录一次 → 系统B 再登录 → 系统C 再登录 ...  （体验差、账号分散）

有 SSO：
  任一系统登录一次 → 系统A/B/C 全部自动登录            （统一身份）
```

## 2. 两个最容易被混淆的概念

### 2.1 认证（Authentication，AuthN）—— 你是谁
确认用户身份的过程，即「证明你是你」。

- 输入账号密码、验证码、指纹、扫码登录
- 回答：**你是谁？**

### 2.2 授权（Authorization，AuthZ）—— 你能做什么
确认用户拥有哪些权限、能访问哪些资源。

- 角色权限、接口访问控制
- 回答：**你被允许做什么？**

> SSO 解决的是 **认证（AuthN）** 的复用问题，而不是授权。
> 常见的 OAuth2 本质是**授权协议**，OIDC 才是基于 OAuth2 的**认证协议**（见下文）。

## 3. 核心角色

| 角色 | 全称 | 说明 |
|------|------|------|
| **IdP** | Identity Provider（身份提供商） | 统一认证中心，负责校验身份、发放凭证。例如公司的 SSO 登录页 |
| **SP** | Service Provider（服务提供商） | 具体的业务系统，信任 IdP 发放的凭证。例如邮箱、OA、Wiki |

SSO 的本质就是：**SP 不自己校验密码，而是信任 IdP 的认证结果**。

## 4. 主流技术方案对比

### 4.1 CAS（Central Authentication Service）
-  Yale 大学开源，最早、最简单的 SSO 协议之一
-  基于「票据（Ticket）」：TGT（票据授予票据）+ ST（服务票据）
-  流程：用户访问 SP → 未登录被重定向到 CAS → 登录后拿到 TGT，CAS 发 ST → SP 拿 ST 去 CAS 校验 → 通过
-  适合传统企业内网系统，协议轻量

### 4.2 SAML（Security Assertion Markup Language）
-  基于 **XML** 的断言（Assertion）标准
-  常用于企业级 B2B，例如对接 Salesforce、企业微信、各类 SaaS
-  采用 SP 发起 / IdP 发起两种流程，通过浏览器重定向 + XML 断言传递身份
-  较重，XML 解析复杂，但在企业市场根深蒂固

### 4.3 OIDC（OpenID Connect）—— 现代主流
-  构建在 **OAuth2 之上** 的身份认证层
-  使用 **JSON / JWT**，比 SAML 的 XML 更轻、更适合移动互联网
-  通过 `id_token`（JWT）携带用户身份，`access_token` 用于授权
-  流程：授权码模式（Authorization Code + PKCE）是目前最推荐的方式

```text
OIDC 授权码流程（简化）：
1. 用户访问 SP → SP 重定向到 IdP 的 /authorize
2. 用户在 IdP 登录并授权
3. IdP 带着 code 重定向回 SP 的回调地址
4. SP 后端用 code 向 IdP 的 /token 换 token
5. IdP 返回 id_token（身份）+ access_token（授权）
6. SP 校验 id_token，建立本地会话
```

### 4.4 OAuth2（授权，不是认证）
-  **OAuth2 本身是授权协议**，解决「第三方应用能否代表用户访问资源」
-  例如「用 GitHub 登录某网站」—— 网站拿到的是**访问你 GitHub 资源的权限**，不是严格的身份认证
-  要用于认证，必须叠加 OIDC 层
-  四种授权模式：授权码（最安全常用）、隐式、密码、客户端凭据

> 关键区别：**OAuth2 回答「能不能访问」，OIDC 回答「你是谁」**。

## 5. 单点登出（SLO，Single Log-Out）

登录可以「一处登录处处通行」，登出也需要「**一处登出处处登出**」。

- **局部会话 / 全局会话**：每个 SP 有自己的局部会话，IdP 持有全局会话
- 登出时，IdP 通知所有已登录的 SP 销毁局部会话（通常通过「后端通知 / 前端回调」）
- 否则会出现：用户在 A 退出，但在 B 系统仍在线的安全漏洞

## 6. 跨域与 Cookie 共享

SSO 常涉及多个不同域名的系统，这是实现难点：

| 场景 | 方案 |
|------|------|
| 同父域（a.x.com / b.x.com） | 把 Cookie 的 domain 设为 `.x.com` 共享 |
| 完全不同域 | 不能共享 Cookie，必须依赖 **中心化 IdP + 重定向票据** 实现 |
| 前端分离架构 | 用 Token（JWT）代替 Cookie 存储状态 |

> 现代 SSO 普遍采用 **Token 方案（JWT）**，天然跨域，不依赖浏览器 Cookie 共享。

## 7. JWT 在 SSO 中的角色

- SSO 发放的 `id_token` / `access_token` 通常是 **JWT（JSON Web Token）**
- JWT 是**自包含**的：签名 + 载荷，SP 用公钥验签即可信任，无需每次回查 IdP
- 结构：`Header.Payload.Signature`
- 注意 JWT 一旦签发难以撤销，需配合短期有效期 + 刷新令牌（Refresh Token）

## 8. 安全注意点（踩坑重点）

- **Token 泄露**：access_token 要短时效，存内存而非 localStorage（防 XSS）
- **CSRF**：授权码流程要校验 `state` 参数，防跨站请求伪造
- **重定向劫持**：严格校验回调 URL 白名单，防止 `redirect_uri` 被篡改
- **票据复用**：CAS 的 ST 只能使用一次，用后作废
- **HTTPS 全程**：凭证在传输中必须加密，明文等于裸奔
- **签名校验**：JWT 必须验签，且禁用 `alg=none` 等不安全算法

## 9. 一句话总结

> SSO 的核心 = **一个可信的 IdP + 一套可复用的认证凭证（Token / 票据）**，
> 让多个 SP 共享「用户已登录」这一事实，从而做到一次登录、处处通行。

现代首选方案：**OIDC（授权码 + PKCE + JWT）**；传统企业对接 SaaS 多见 **SAML**；轻量内网可用 **CAS**。

## 10. 相关概念跳转

- 认证 vs 授权：见上文 [[#2. 两个最容易被混淆的概念]]
- Token 细节：见 [[JWT]]
- 协议选型：[[OAuth2]] / [[OIDC]] / [[SAML]] / [[CAS]]
- 登出机制：见 [[#6. 单点登出（SLO，Single Log-Out）]]
