"""Local educational sales API. Synthetic data only; not a production server."""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FIXTURES = json.loads(Path(__file__).with_name("fixtures.json").read_text(encoding="utf-8"))
MODES = {"normal", "server_error", "rate_limit", "invalid_json", "invalid_schema", "timeout"}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Never log headers, tokens or request query strings.
        pass

    def respond(self, status, payload, extra=None, raw=False):
        body = payload.encode("utf-8") if raw else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def error(self, status, code):
        self.respond(status, {"error": {"code": code}})

    def do_GET(self):
        request = urlparse(self.path)
        if request.path == "/health":
            return self.respond(200, {"status": "ok"})
        if request.path not in ("/v1/customers", "/v1/orders"):
            return self.error(404, "not_found")
        token = os.environ.get("SALES_API_TOKEN", "local-training-only")
        if self.headers.get("Authorization") != "Bearer " + token:
            return self.error(401, "unauthorized")
        query = parse_qs(request.query, keep_blank_values=True)
        if set(query) - {"page", "per_page", "revision", "mode", "fail_page"} or any(len(v) != 1 for v in query.values()):
            return self.error(400, "invalid_query")
        try:
            page = int(query.get("page", ["1"])[0])
            per_page = int(query.get("per_page", ["2"])[0])
            fail_page = int(query.get("fail_page", ["0"])[0])
            if page < 1 or not 1 <= per_page <= 100 or fail_page < 0:
                raise ValueError()
        except ValueError:
            return self.error(400, "invalid_pagination")
        revision = query.get("revision", ["1"])[0]
        mode = query.get("mode", ["normal"])[0]
        if revision not in FIXTURES["revisions"] or mode not in MODES:
            return self.error(400, "invalid_query")
        if fail_page and page == fail_page:
            return self.error(503, "temporary_failure")
        if mode == "server_error":
            return self.error(503, "temporary_failure")
        if mode == "rate_limit":
            return self.respond(429, {"error": {"code": "rate_limited"}}, {"Retry-After": "2"})
        if mode == "invalid_json":
            return self.respond(200, '{"data":', raw=True)
        if mode == "invalid_schema":
            return self.respond(200, {"data": [{"order_id": None, "amount": "not-an-integer"}]})
        if mode == "timeout":
            time.sleep(3)
        dataset = FIXTURES["revisions"][revision]
        rows = FIXTURES["customers"] if request.path.endswith("customers") else dataset["orders"]
        start = (page - 1) * per_page
        self.respond(200, {
            "data": rows[start:start + per_page],
            "meta": {"page": page, "per_page": per_page, "total": len(rows),
                     "next_page": page + 1 if start + per_page < len(rows) else None,
                     "revision": int(revision), "snapshot_at": dataset["snapshot_at"]}
        })

if __name__ == "__main__":
    server = ThreadingHTTPServer((os.environ.get("BIND_HOST", "127.0.0.1"), int(os.environ.get("PORT", "8099"))), Handler)
    print("Synthetic sales API ready", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
