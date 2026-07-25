# syntax=docker/dockerfile:1
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y samba && rm -rf /var/lib/apt/lists/*

RUN useradd -M -s /usr/sbin/nologin backupuser && \
    useradd -M -s /usr/sbin/nologin eskil

RUN --mount=type=secret,id=samba_secrets \
    BACKUP_PASS=$(sed -n '1p' /run/secrets/samba_secrets) && \
    ESKIL_PASS=$(sed -n '2p' /run/secrets/samba_secrets) && \
    (echo "$BACKUP_PASS"; echo "$BACKUP_PASS") | smbpasswd -a -s backupuser && \
    (echo "$ESKIL_PASS"; echo "$ESKIL_PASS") | smbpasswd -a -s eskil

COPY smb.conf /etc/samba/smb.conf
EXPOSE 445
CMD ["smbd", "--foreground", "--no-process-group"]