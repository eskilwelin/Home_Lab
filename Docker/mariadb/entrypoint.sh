#!/bin/bash
set -e
usermod -aG backupuser eskil
chown backupuser:backupuser /share
chmod 750 /share
service cron start
exec smbd --foreground --no-process-group