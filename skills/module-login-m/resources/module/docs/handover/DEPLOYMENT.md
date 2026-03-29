# 部署手册（测试服）

## 1. 前置条件
- 本机存在 Docker context：`ark-server`
- 资源文件存在：`../docs/resource/email.md`
- 可访问测试服务器：`115.190.174.181`

## 2. 关键文件
- 编排：`deploy/docker-compose.test.yml`
- 前端镜像：`deploy/Dockerfile.frontend`
- 前端 Nginx：`deploy/nginx.frontend.conf`
- 后端镜像：`Dockerfile`

## 3. 部署步骤
```bash
cd /Users/zxf/GitHub/modules/login_m
# 已有 deploy/.env.test（SMTP_USER/SMTP_PASS/SMTP_FROM）
docker --context ark-server compose -f deploy/docker-compose.test.yml --env-file deploy/.env.test up -d --build
```

## 4. 服务映射
- `18000 -> login-m-api-test:8000`
- `18100 -> login-m-web-test:80`
- `13306 -> login-m-mysql-test:3306`

## 5. 回滚
```bash
# 查看历史镜像并指定旧镜像 tag 回退
docker --context ark-server images
# 修改 compose image 后重新 up -d
```
