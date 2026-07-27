#!/bin/bash
set -e

DATE=$(date +%Y-%m-%d_%H%M%S)
DBPW=$(cat /run/secrets/db_secrets)
DB_NAME=${1:-DefaultDB}

mariadb-dump \
  --host=database \
  --port=3306 \
  --user=dbuser \
  --password="$DBPW" \
  --single-transaction \
  --databases $DB_NAME > /share/db_backup_${DATE}.sql