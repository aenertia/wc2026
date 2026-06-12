#!/usr/bin/env python3
"""
Local server for the World Cup 2026 wallchart.
Serves static files and proxies:
  /api/espn   → ESPN scoreboard (live scores, results)
  /api/*      → worldcup26.ir (group standings, team flags)
Usage: python3 server.py [port]   (default port: 8191)
"""
import http.server, subprocess, os, sys, time, threading, logging
from datetime import date

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8191
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
WC_API_BASE = "https://worldcup26.ir/get"
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
TOURNAMENT_START = "20260611"
CACHE_TTL = 60  # seconds

_cache: dict = {}
_cache_lock = threading.Lock()

def fetch_url(url: str, cache_key: str) -> bytes:
    with _cache_lock:
        entry = _cache.get(cache_key)
        if entry and time.time() - entry["ts"] < CACHE_TTL:
            return entry["data"]

    result = subprocess.run(
        ["curl", "-s", "--max-time", "10", "-H", "Accept: application/json", url],
        capture_output=True, timeout=12
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl exit {result.returncode}")

    with _cache_lock:
        _cache[cache_key] = {"data": result.stdout, "ts": time.time()}
    return result.stdout


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/api/espn":
            today = date.today().strftime("%Y%m%d")
            url = f"{ESPN_BASE}?dates={TOURNAMENT_START}-{today}"
            try:
                data = fetch_url(url, "espn")
                self._send_json(data)
            except Exception as e:
                self.send_error(502, f"ESPN proxy error: {e}")
        elif self.path.startswith("/api/"):
            endpoint = self.path[5:]  # strip /api/
            url = f"{WC_API_BASE}/{endpoint}"
            try:
                data = fetch_url(url, endpoint)
                self._send_json(data)
            except Exception as e:
                self.send_error(502, f"Proxy error: {e}")
        else:
            super().do_GET()

    def _send_json(self, data: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        logging.info("%s - - [%s] %s", self.address_string(),
                     self.log_date_time_string(), fmt % args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    httpd = http.server.ThreadingHTTPServer(("", PORT), Handler)
    print(f"Serving on http://localhost:{PORT}", flush=True)
    httpd.serve_forever()
