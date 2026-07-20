#!/bin/bash
for dir in ~/docker/*/; do
  echo "Updating $dir"
  docker compose -f "$dir/compose.yml" pull
  docker compose -f "$dir/compose.yml" up -d
done