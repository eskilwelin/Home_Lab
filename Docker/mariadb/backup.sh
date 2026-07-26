#!/bin/bash

DATE=$(date +%Y-%m-%d_%H%M%S)
DBPW=/run/secrets/db_secrets

if $Running; then 
    mariadb-backup --backup \
    --target-dir=/var/mariadb/backup/ \
    --databases='DefaultDB'
    --user=dbuser --password=$DBPW

    if (mv /var/mariadb/backup/* /share/db_backup/)
        echo "[$DATE] SUCCESS: Backup saved." >> /share/db_logs/backup_history.log
    fi
fi