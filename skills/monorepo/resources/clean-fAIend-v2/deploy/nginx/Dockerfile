FROM nginx:1.27-alpine
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
# 将证书目录一并打进镜像（可在本地放置 pem/key）
COPY ssl/ /etc/nginx/ssl/
