# SSL 证书目录

此目录用于存放 SSL 证书文件。

## 开发环境

使用自签名证书：

```bash
# Linux/Mac
bash scripts/generate-ssl-cert.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/generate-ssl-cert.ps1
```

生成的文件：
- `cert.pem` - 证书文件
- `key.pem` - 私钥文件

**注意：** 自签名证书会在浏览器中显示安全警告，这是正常的。

## 生产环境

生产环境应使用受信任的 CA 颁发的证书，推荐使用 Let's Encrypt（免费）：

### 方法一：使用 Certbot（推荐）

```bash
# 安装 certbot
sudo apt-get update
sudo apt-get install certbot

# 获取证书（需要域名和 DNS 解析）
sudo certbot certonly --standalone -d yourdomain.com

# 证书文件通常位于：
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# 复制到当前目录
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

### 方法二：手动上传证书

如果有其他来源的证书，将以下文件放置在此目录：

- `cert.pem` - 证书文件（或证书链文件）
- `key.pem` - 私钥文件

### 证书续期（Let's Encrypt）

Let's Encrypt 证书有效期为 90 天，需要定期续期：

```bash
# 手动续期
sudo certbot renew

# 设置自动续期（crontab）
# 每月检查并续期
0 0 1 * * certbot renew --quiet && docker-compose restart nginx
```

或者使用 Docker 容器自动续期（推荐在生产环境使用）。

## 安全建议

1. **私钥文件权限**：确保 `key.pem` 文件权限为 600
   ```bash
   chmod 600 ssl/key.pem
   ```

2. **不要提交私钥**：确保 `.gitignore` 中包含 `ssl/*.pem` 或 `ssl/key.pem`

3. **定期更新证书**：生产环境证书过期前及时续期

4. **使用强加密**：证书密钥长度至少 2048 位（RSA）或使用 ECDSA

