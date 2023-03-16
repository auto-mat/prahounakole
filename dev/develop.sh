#!/usr/bin/env bash
docker-compose down
docker-compose up -d
exec docker exec -it prahounakole_web_1 bash --init-file ./dev/docker-dev-entrypoint.sh
