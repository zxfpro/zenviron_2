#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env initialized from .env.example"
else
  echo ".env already exists"
fi

echo "Run: docker compose up -d --build"
