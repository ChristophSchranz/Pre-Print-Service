#!/usr/bin/env bash
docker-compose build
docker-compose push || true
docker stack deploy --compose-file docker-compose.yml tweaker
