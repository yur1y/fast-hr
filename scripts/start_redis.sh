#!/usr/bin/env bash
set -euo pipefail

REDIS_HOST="localhost"
REDIS_PORT="6379"

start_with_docker() {
  if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    return 1
  fi
  echo "Starting Redis via Docker Compose..."
  cd /home/ur/workspace/personal/tracepilot/docker
  docker compose up -d redis
  cd - >/dev/null || true
  return 0
}

start_local_redis() {
  if command -v redis-server >/dev/null 2>&1; then
    echo "Starting local Redis..."
    redis-server --daemonize yes --bind "${REDIS_HOST}" --port "${REDIS_PORT}"
    return 0
  fi
  echo "Local Redis not found."
  return 1
}

wait_for_redis() {
  echo "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
  for i in $(seq 1 30); do
    if (echo >/dev/tcp/${REDIS_HOST}/${REDIS_PORT}) 2>/dev/null; then
      echo "Port ${REDIS_PORT} is open."
      return 0
    fi
    sleep 1
  done
  echo "Timed out waiting for port ${REDIS_PORT}."
  return 1
}

main() {
  if (echo >/dev/tcp/${REDIS_HOST}/${REDIS_PORT}) 2>/dev/null; then
    echo "Redis is already running on ${REDIS_HOST}:${REDIS_PORT}."
    exit 0
  fi

  if start_with_docker; then
    echo "Docker Redis started."
  else
    start_local_redis || {
      echo "Failed to start Redis via any available method."
      exit 1
    }
  fi

  wait_for_redis

  echo "Redis is ready at ${REDIS_HOST}:${REDIS_PORT}."
}

main "$@"
