from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

ROOT_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
os.chdir(ROOT_DIR)


def find_free_port(start: int = 8000, end: int = 8100) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port available between 8000 and 8100")


def run_server(port: int) -> None:
    config = uvicorn.Config(
        app="backend.app:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    server.run()


def wait_for_server(port: int, timeout: float = 20.0) -> bool:
    started = time.time()
    while time.time() - started < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def main() -> None:
    port = find_free_port()
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    ok = wait_for_server(port)
    url = f"http://127.0.0.1:{port}"

    if not ok:
        raise RuntimeError("Neo AI Report App server failed to start")

    try:
        import webview  # type: ignore
        webview.create_window("Neo AI Report App", url, width=1440, height=940, min_size=(1100, 720))
        webview.start()
    except Exception:
        webbrowser.open(url)
        print(f"Neo AI Report App started at {url}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
