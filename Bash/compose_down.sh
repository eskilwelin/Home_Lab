#!/bin/bash
for dir in ~/docker/*/;do
    echo "Shutting down $dir"
    docker compose -f "$dir/compose.yml" down
done