from __future__ import annotations

import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

import uvicorn

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))


def write_log(text: str) -> None:
    try:
        log_file = APP_DIR / "neo_ai_report_app_error.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass


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
    try:
        if str(BUNDLE_DIR) not in sys.path:
            sys.path.insert(0, str(BUNDLE_DIR))

        from backend.app import app as fastapi_app

        config = uvicorn.Config(
            app=fastapi_app,
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="info",
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception:
        write_log("=== SERVER START ERROR ===")
        write_log(traceback.format_exc())
        raise


def wait_for_server(port: int, timeout: float = 60.0) -> bool:
    started = time.time()
    while time.time() - started < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def main() -> None:
    try:
        os.chdir(APP_DIR)

        port = find_free_port()
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()

        ok = wait_for_server(port)
        url = f"http://127.0.0.1:{port}"

        if not ok:
            raise RuntimeError(
                f"Neo AI Report App server failed to start. Check log: {APP_DIR / 'neo_ai_report_app_error.log'}"
            )

        try:
            import webview  # type: ignore

            webview.create_window(
                "Neo AI Report App",
                url,
                width=1440,
                height=940,
                min_size=(1100, 720),
            )
            webview.start()
        except Exception:
            webbrowser.open(url)
            while True:
                time.sleep(1)

    except Exception:
        write_log("=== LAUNCHER ERROR ===")
        write_log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
