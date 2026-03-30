#!/bin/bash

DEFAULT_COMMIT_MESSAGE="Auto build and publish "
COMMIT_MESSAGE=$(printf "%s\n%s" "$PYTHON_OUTPUT" "${1:-$DEFAULT_COMMIT_MESSAGE}")

# 添加 git commit 功能
# 检查当前是否在 git 仓库中 (可选，但建议)
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  # 添加所有更改的文件到暂存区
  git add .
  # 提交更改，使用获取到的 commit 信息
  git commit -m "$COMMIT_MESSAGE"
  echo "Git commit successful with message: \"$COMMIT_MESSAGE\""
else
  echo "Not inside a git repository. Skipping git commit."
fi


# 获取当前 Git 仓库的提交次数作为版本号的一部分
# 如果不在 Git 仓库中，或者没有提交，则使用默认值
GIT_COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

# 获取当前日期作为版本号的一部分，格式为 YYYYMMDD
DATE_VERSION=$(date +%Y%m%d)


DOCKER_VERSION="${DATE_VERSION}-${GIT_COMMIT_COUNT}"
echo "Building Docker image with version: ${DOCKER_VERSION}"

# TOOD 
docker buildx build --platform linux/amd64,linux/arm64 \
  -t 823042332/digital_life:${DOCKER_VERSION} \
  -t 823042332/digital_life:latest . --push
