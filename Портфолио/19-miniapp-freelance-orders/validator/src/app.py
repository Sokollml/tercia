"""Опциональный HTTP-микросервис валидации initData (stdlib, без зависимостей).

Нужен, только если ты хочешь выносить проверку initData из n8n Code-ноды в
отдельный сервис (например, чтобы не дублировать секрет бота в воркфлоу).
По умолчанию api.json валидирует initData сам, и этот сервис НЕ обязателен.

POST /validate  { "init_data": "<raw initData>" }
  -> 200 { "ok": true, "user_id": 123, "user": {...} }
  -> 401 { "ok": false, "reason": "bad_hash" }

BOT_TOKEN и INITDATA_MAX_AGE берутся из окружения.
Запуск:  python -m src.app   (слушает VALIDATOR_PORT, по умолчанию 8081)
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from initdata import validate_init_data

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_AGE = int(os.getenv("INITDATA_MAX_AGE", "86400"))
PORT = int(os.getenv("VALIDATOR_PORT", "8081"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/validate":
            self._send(404, {"ok": False, "reason": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "reason": "bad_json"})
            return

        result = validate_init_data(
            data.get("init_data", ""), BOT_TOKEN, max_age_seconds=MAX_AGE
        )
        if result.ok:
            self._send(200, {"ok": True, "user_id": result.user_id, "user": result.user})
        else:
            self._send(401, {"ok": False, "reason": result.reason})

    def log_message(self, *_a):  # тише в консоли
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"initData validator слушает :{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
