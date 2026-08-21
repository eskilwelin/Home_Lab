#!/usr/bin/env python3
"""Multi-user TCP chat server: one handler thread per client, newline-delimited UTF-8.

Messages and join/leave events are appended to a transcript file as they happen,
so conversations stay readable after the clients that produced them disconnect.
"""

# Plaintext protocol with no authentication or encryption -- for trusted networks only.

import argparse
import logging
import os
import socket
import threading
import time

clients = {}  # socket -> nickname
clients_lock = threading.Lock()


def log(text):
    """Echo an event to the console and append it to the transcript."""
    print(text)
    logging.info(text)


def open_transcript(log_dir):
    """Start a timestamped transcript in log_dir, falling back to ./shutup-logs if it is unwritable."""
    name = time.strftime("shutup-%Y%m%d-%H%M%S.log")
    try:
        os.makedirs(log_dir, exist_ok=True)
        handler = logging.FileHandler(os.path.join(log_dir, name), encoding="utf-8")
    except OSError as exc:
        log_dir = os.path.abspath("shutup-logs")
        print(f"! cannot write to {exc.filename}: {exc.strerror} -- logging to {log_dir} instead")
        os.makedirs(log_dir, exist_ok=True)
        handler = logging.FileHandler(os.path.join(log_dir, name), encoding="utf-8")

    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)  # flushes per record, so an abrupt kill loses nothing
    return handler.baseFilename


def send_line(conn, text):
    """Write one newline-terminated UTF-8 line, ignoring already-dead sockets."""
    try:
        conn.sendall((text + "\n").encode("utf-8"))
    except OSError:
        pass


def broadcast(text, exclude=None):
    """Send text to every registered client except `exclude`."""
    with clients_lock:
        targets = [conn for conn in clients if conn is not exclude]
    for conn in targets:
        send_line(conn, text)


def read_lines(conn):
    """Yield complete lines from conn, buffering partial recv() reads."""
    buffer = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            return
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            yield line.decode("utf-8", errors="replace").rstrip("\r")


def handle_client(conn, addr):
    """Register the client from its first line (the nickname), then relay its messages."""
    nickname = None
    try:
        lines = read_lines(conn)
        nickname = next(lines, "").strip()
        if not nickname:
            return
        with clients_lock:
            clients[conn] = nickname
        log(f"* {nickname} joined from {addr[0]}:{addr[1]}")
        send_line(conn, f"* welcome, {nickname}")
        broadcast(f"* {nickname} joined", exclude=conn)

        for line in lines:
            if line:
                message = f"{nickname}: {line}"
                log(message)
                broadcast(message, exclude=conn)
    except OSError:
        pass  # abrupt disconnect: fall through to cleanup
    finally:
        with clients_lock:
            was_registered = clients.pop(conn, None) is not None
        conn.close()
        if was_registered:
            log(f"* {nickname} left")
            broadcast(f"* {nickname} left")


def main():
    parser = argparse.ArgumentParser(description="Minimal multi-user TCP chat server.")
    parser.add_argument("--host", default="0.0.0.0", help="bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9000, help="bind port (default: 9000)")
    parser.add_argument("--log-dir", default="/var/log/shutup",
                        help="transcript directory (default: /var/log/shutup)")
    args = parser.parse_args()

    transcript = open_transcript(args.log_dir)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen()
    log(f"listening on {args.host}:{args.port} -- transcript: {transcript}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        log("shutting down")
    finally:
        server.close()
        logging.shutdown()


if __name__ == "__main__":
    main()
