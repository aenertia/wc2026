#!/usr/bin/env python3
"""
Local server for the World Cup 2026 wallchart.
Serves static files and proxies /api/* to worldcup26.ir to avoid CORS.
Usage: python3 server.py [port]   (default port: 8191)
"""
import http.server, subprocess, os, sys, time, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8191
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://worldcup26.ir/get"
CACHE_TTL = 60  # seconds

_cache: dict = {}
_cache_lock = threading.Lock()

def fetch_api(endpoint: str) -> bytes:
    with _cache_lock:
        entry = _cache.get(endpoint)
        if entry and time.time() - entry["ts"] < CACHE_TTL:
            return entry["data"]

    result = subprocess.run(
        ["curl", "-s", "--max-time", "10", "-H", "Accept: application/json",
         f"{API_BASE}/{endpoint}"],
        capture_output=True, timeout=12
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl exit {result.returncode}")

    with _cache_lock:
        _cache[endpoint] = {"data": result.stdout, "ts": time.time()}
    return result.stdout


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            endpoint = self.path[5:]  # strip /api/
            try:
                data = fetch_api(endpoint)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(502, f"Proxy error: {e}")
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        pass  # suppress request noise in the log file


if __name__ == "__main__":
    httpd = http.server.ThreadingHTTPServer(("", PORT), Handler)
    print(f"Serving on http://localhost:{PORT}", flush=True)
    httpd.serve_forever()
