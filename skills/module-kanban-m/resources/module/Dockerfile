
# docker buildx build --platform linux/amd64,linux/arm64 -t 823042332/digital_life:1.5 -t 823042332/digital_life:latest . --push
# ARG VERSION=1.6
# 使用官方 Python 3.10 镜像
# --- 公共构建阶段：安装公共依赖 ---
# --- 第一阶段：构建阶段 ---
    
# FROM python:3.12-slim AS builder
FROM ac2-registry.cn-hangzhou.cr.aliyuncs.com/ac2/base:ubuntu24.04-py312 AS builder

RUN pip install --no-cache-dir aiomysql \
                                volcengine-python-sdk==4.0.6 \
                                fastapi==0.119.1 \
                                qdrant-client==1.15.1 \
                                redis==7.0.0 \
                                uvicorn==0.38.0 \
                                sqlalchemy==2.0.44 \
                                -i https://pypi.tuna.tsinghua.edu.cn/simple -i https://mirrors.aliyun.com/pypi/simple/


# --- 第三阶段：最终运行环境 ---
# FROM python:3.12-slim
FROM ac2-registry.cn-hangzhou.cr.aliyuncs.com/ac2/base:ubuntu24.04-py312

# 阿里云本地镜像无法编译这个, 只有在正式编译时(CICD放开
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends vim && \
#     apt-get clean && 

COPY --from=builder /opt/ac2/lib/python3.12/site-packages /opt/ac2/lib/python3.12/site-packages


## digital_life
WORKDIR /app
COPY ./src /app/src
COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock

RUN pip install -e /app -i https://pypi.tuna.tsinghua.edu.cn/simple -i https://mirrors.aliyun.com/pypi/simple/


# 暴露应用运行的端口
EXPOSE 80

# 设置默认命令启动 FastAPI 应用
