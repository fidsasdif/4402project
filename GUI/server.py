"""Serves the GUI and connects it to data.db (built by generate_data.py from schema.sql).
Standard library only: python gui/server.py  ->  http://127.0.0.1:8000"""
import json
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "data.db"  # same file generate_data.py writes
WRITE_VERBS = ("INSERT", "UPDATE")  # the UI never deletes or alters the schema


def connect(read_only):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if read_only:
        conn.execute("PRAGMA query_only = ON")
    return conn


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, payload, ctype="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.reply(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if self.path == "/api/query":
                sql = data["sql"]
                if not sql.lstrip().upper().startswith("SELECT"):
                    raise ValueError("only SELECT is allowed here")
                conn = connect(True)
                try:
                    rows = [dict(r) for r in conn.execute(sql, data.get("params", []))]
                finally:
                    conn.close()
                self.reply(200, {"rows": rows})
            elif self.path == "/api/exec":  # all statements commit together or not at all
                conn = connect(False)
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    for sql, params in data["stmts"]:
                        if sql.lstrip().split(None, 1)[0].upper() not in WRITE_VERBS:
                            raise ValueError("only INSERT and UPDATE are allowed")
                        conn.execute(sql, params)  # execute() runs a single statement only
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "not found"})
        except Exception as exc:  # constraint violations etc. go back to the UI as a message
            self.reply(400, {"error": str(exc)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not DB_PATH.exists():
        sys.exit(f"{DB_PATH} not found. Run `python generate_data.py` first.")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"GUI on http://127.0.0.1:{port}  (database: {DB_PATH})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
