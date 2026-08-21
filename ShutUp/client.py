#!/usr/bin/env python3
"""CLI chat client: a receiver thread prints incoming lines while the main thread reads stdin."""

# Plaintext protocol with no authentication or encryption -- for trusted networks only.

import argparse
import os
import socket
import threading


def receive_loop(sock):
    """Print server lines as they arrive, buffering partial recv() reads."""
    buffer = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                print(line.decode("utf-8", errors="replace").rstrip("\r"))
    except OSError:
        pass
    print("* disconnected from server")
    # The main thread is parked in input(); exit the process outright rather than wait for it.
    os._exit(0)


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI chat client.")
    parser.add_argument("--host", default="127.0.0.1", help="server address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, help="server port (default: 9000)")
    args = parser.parse_args()

    try:
        nickname = ""
        while not nickname:
            nickname = input("nickname: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    sock = socket.create_connection((args.host, args.port))
    sock.sendall((nickname + "\n").encode("utf-8"))
    print(f"* connected to {args.host}:{args.port} -- type /quit to exit")

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    try:
        while True:
            line = input().strip()
            if line == "/quit":
                break
            if line:
                sock.sendall((line + "\n").encode("utf-8"))
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    finally:
        sock.close()
        print("\n* bye")


if __name__ == "__main__":
    main()
