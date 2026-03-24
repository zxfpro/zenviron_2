.PHONY: help build up down restart logs clean test

help:
	@echo "Tool Server - 可用命令:"
	@echo "  make build       - 构建Docker镜像"
	@echo "  make up          - 启动所有服务"
	@echo "  make down        - 停止所有服务"
	@echo "  make restart     - 重启所有服务"
	@echo "  make logs        - 查看日志"
	@echo "  make clean       - 清理容器和数据卷"
	@echo "  make test        - 运行测试"
	@echo "  make db-init     - 初始化数据库"
	@echo "  make db-migrate  - 执行数据库迁移"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "服务已启动，访问 http://localhost:5000"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	@echo "已清理所有容器和数据卷"

test:
	@echo "运行测试..."
	python -m pytest tests/

db-init:
	docker-compose exec app python scripts/init_db.py
	@echo "数据库初始化完成"

db-migrate:
	@echo "FastAPI版本使用 init_db.py 初始化数据库"

