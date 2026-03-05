#!/usr/bin/env python3
"""
server.py — Веб-сервер IDE для языка ПОВЕЛЕВАЮ
Запуск: python server.py
Затем открой http://localhost:8000 в браузере
"""

import sys
import os
import json
import subprocess
import tempfile
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent
IDE_DIR  = BASE_DIR / "ide"
PORT     = 8000

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".ico":  "image/x-icon",
    ".pov":  "text/plain; charset=utf-8",
}


class IDEHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Тихий режим — только ошибки
        if args and str(args[1]) not in ("200", "304"):
            print(f"  {args[0]}  {args[1]}", file=sys.stderr)

    # ── GET ─────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split("?")[0]

        # Корень → index.html
        if path in ("/", ""):
            path = "/index.html"

        # Примеры: /examples/<file>.pov
        if path.startswith("/examples/"):
            file_path = BASE_DIR / path.lstrip("/")
        else:
            file_path = IDE_DIR / path.lstrip("/")

        if file_path.is_file():
            self._serve_file(file_path)
        else:
            self._send(404, "text/plain", b"404 Not Found")

    # ── POST ────────────────────────────────────────────
    def do_POST(self):
        if self.path != "/api/run":
            self._send(404, "text/plain", b"Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data  = json.loads(body)
            code  = data.get("code", "")
            stdin = data.get("stdin", "")
        except (json.JSONDecodeError, KeyError) as e:
            self._json({"error": f"Неверный запрос: {e}"}, 400)
            return

        result = self._run_code(code, stdin)
        self._json(result)

    # ── Запуск программы ────────────────────────────────
    def _run_code(self, code: str, stdin: str) -> dict:
        tmp = None
        try:
            # Пишем код во временный файл
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pov", encoding="utf-8",
                delete=False, dir=BASE_DIR
            ) as f:
                f.write(code)
                tmp = f.name

            proc = subprocess.run(
                [sys.executable, str(BASE_DIR / "main.py"), tmp],
                input=stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
                cwd=str(BASE_DIR),
            )

            stdout = proc.stdout or ""
            stderr = proc.stderr or ""

            # stderr идёт в отдельное поле (для ошибок интерпретатора)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": proc.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "⚔ Свиток исполнялся слишком долго и был прерван",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"⚔ Внутренняя ошибка сервера: {e}",
                "returncode": -1,
            }
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

    # ── Вспомогательные ─────────────────────────────────
    def _serve_file(self, path: Path):
        suffix = path.suffix.lower()
        mime   = MIME.get(suffix, "application/octet-stream")
        data   = path.read_bytes()
        self._send(200, mime, data)

    def _json(self, obj: dict, code: int = 200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(code, "application/json; charset=utf-8", data)

    def _send(self, code: int, mime: str, data: bytes):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ── Запуск ──────────────────────────────────────────────
def open_browser(port):
    import time
    time.sleep(0.8)
    webbrowser.open(f"http://localhost:{port}")

def main():
    server = HTTPServer(("localhost", PORT), IDEHandler)

    print(f"""
╔══════════════════════════════════════════════╗
║       ПОВЕЛЕВАЮ — IDE  v1.0                  ║
╠══════════════════════════════════════════════╣
║  Сервер запущен:  http://localhost:{PORT}      ║
║  Остановить:      Ctrl+C                     ║
╚══════════════════════════════════════════════╝
""")

    # Открываем браузер автоматически
    threading.Thread(target=open_browser, args=(PORT,), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n— Сервер остановлен. Прощай! —")


if __name__ == "__main__":
    main()
