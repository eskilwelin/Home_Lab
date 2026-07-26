#!/bin/bash
set -e
service cron start
exec smbd --foreground --no-process-group