# 运维与排障

## 1. 常用检查
```bash
docker --context ark-server ps
curl http://115.190.174.181:18000/health
```

## 2. 查看日志
```bash
docker --context ark-server logs -f login-m-api-test
docker --context ark-server logs -f login-m-web-test
docker --context ark-server logs -f login-m-mysql-test
```

## 3. 数据库连接
- Host: `115.190.174.181`
- Port: `13306`
- User: `root`
- Password: `1234`
- DB: `login_m`

```bash
mysql -h 115.190.174.181 -P 13306 -u root -p1234
```

## 4. 常见问题
- 手机验证码接口 200 但收不到短信：短信通道仍为 mock/webhook 未落地。
- 前端打不开：检查 18100 端口是否被安全组/防火墙放通。
- MySQL 不健康：先看 `login-m-mysql-test` 日志，再检查旧卷兼容问题。
