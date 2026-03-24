## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd tool
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，配置数据库密码、Redis等
# 重要：生产环境必须修改以下配置：
#   - SECRET_KEY: 应用密钥
#   - DB_PASSWORD: 数据库密码
#   - REDIS_PASSWORD: Redis密码（如果需要）
```

3. **初始化数据库**
```bash
# 使用快速建表脚本（推荐）
python scripts/init_db_mysql.py

# 或手动执行 SQL 文件
mysql -u root -p test_db < migrations/init_all_tables.sql

```

4. **启动服务**
```bash
docker-compose up -d
```

5. **验证服务**
```bash
# 健康检查
curl http://localhost/api/v1/health

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 方式二：本地开发

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
# 复制并编辑环境变量
cp env.example .env

# 或直接设置环境变量
export APP_ENV=development
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=test_db
```

3. **初始化数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 使用快速建表脚本
python scripts/init_db_mysql.py

# 或手动执行 SQL
mysql -u root -p test_db < migrations/init_all_tables.sql
```

4. **启动服务**
```bash
# 开发模式（自动重载）
python main.py

# 生产模式
gunicorn -c gunicorn_config.py main:app
```



