#!/usr/bin/env python3
"""Multi-user TCP chat server: one handler thread per client, newline-delimited UTF-8."""

# Plaintext protocol with no authentication or encryption -- for trusted networks only.

import argparse
import socket
import threading

clients = {}  # socket -> nickname
clients_lock = threading.Lock()


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
        print(f"* {nickname} connected from {addr[0]}:{addr[1]}")
        send_line(conn, f"* welcome, {nickname}")
        broadcast(f"* {nickname} joined", exclude=conn)

        for line in lines:
            if line:
                broadcast(f"{nickname}: {line}", exclude=conn)
    except OSError:
        pass  # abrupt disconnect: fall through to cleanup
    finally:
        with clients_lock:
            was_registered = clients.pop(conn, None) is not None
        conn.close()
        if was_registered:
            print(f"* {nickname} disconnected")
            broadcast(f"* {nickname} left")


def main():
    parser = argparse.ArgumentParser(description="Minimal multi-user TCP chat server.")
    parser.add_argument("--host", default="0.0.0.0", help="bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9000, help="bind port (default: 9000)")
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen()
    print(f"listening on {args.host}:{args.port}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.close()


if __name__ == "__main__":
    main()
