
# 数据库服务配置文档

本文档仅保留当前项目需要关注的数据库配置信息：[`qdrant`](docs/resource/sql-info/database-config.md:8) 与 [`mysql`](docs/resource/sql-info/database-config.md:27)。

## 概述

| 服务 | 类型 | 主机端口 | 容器端口 | 用途 |
|------|------|----------|----------|------|
| qdrant | Qdrant | 6333 | 6333 | 向量数据库 |
| mysql | MySQL | 3306 | 3306 | 关系型数据库 |

---

## 1. Qdrant 数据库

### 基本信息
- **服务名称**: `qdrant`
- **镜像**: `qdrant/qdrant:latest`
- **主机端口**: `6333`
- **容器端口**: `6333`
- **容器名称**: `qdrant`

### 数据持久化
- **数据卷映射**:
  ```yaml
  /Users/zxf/Documents/SQLDATA/qdrant:/qdrant/data
  ```
- **数据目录**: `/Users/zxf/Documents/SQLDATA/qdrant`

### 连接信息
- **内部 URL**: `http://qdrant:6333`
- **外部访问**: `http://localhost:6333`
- **容器内访问**: `http://qdrant:6333`

---

## 2. MySQL 数据库

### 基本信息
- **服务名称**: `mysql`
- **镜像**: `mysql:latest`
- **主机端口**: `3306`
- **容器端口**: `3306`
- **容器名称**: `mysql`

### 认证配置
- **默认用户**: `root`
- **Root 密码**: `1234`

### 数据持久化
- **数据卷映射**:
  ```yaml
  /Users/zxf/Documents/SQLDATA/mysql:/var/lib/mysql
  ```
- **数据目录**: `/Users/zxf/Documents/SQLDATA/mysql`

### 连接信息
- **主机**: `localhost`
- **端口**: `3306`
- **用户**: `root`
- **密码**: `1234`
- **连接字符串示例**:
  ```python
  import mysql.connector

  conn = mysql.connector.connect(
      host="localhost",
      port=3306,
      user="root",
      password="1234",
  )
  ```
- **命令行连接示例**:
  ```bash
  mysql -h localhost -P 3306 -u root -p1234
  ```


# 云端数据库

Qdrant 测试向量库
  39.96.146.47:5333