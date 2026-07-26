# syntax=docker/dockerfile:1
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y samba cron mariadb-client && rm -rf /var/lib/apt/lists/*

RUN useradd -M -s /bin/bash backupuser && \
    useradd -M -s /usr/sbin/nologin eskil

RUN --mount=type=secret,id=samba_secrets \
    BACKUP_PASS=$(sed -n '1p' /run/secrets/samba_secrets) && \
    ESKIL_PASS=$(sed -n '2p' /run/secrets/samba_secrets) && \
    (echo "$BACKUP_PASS"; echo "$BACKUP_PASS") | smbpasswd -a -s backupuser && \
    (echo "$ESKIL_PASS"; echo "$ESKIL_PASS") | smbpasswd -a -s eskil

RUN echo "0 22 * * * backupuser /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1" >> /etc/cron.d/backup-cron

COPY entrypoint.sh /entrypoint.sh
COPY backup.sh /usr/local/bin/backup.sh
COPY smb.conf /etc/samba/smb.conf
RUN chmod +x /entrypoint.sh /usr/local/bin/backup.sh

EXPOSE 445
ENTRYPOINT ["/entrypoint.sh"]