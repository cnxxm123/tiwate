"""
提瓦特放置 - Web 版服务器
静态文件服务 + 存档 API，默认端口 8080
"""
import json
import os
import http.server
import socketserver
import urllib.parse

PORT = 8080
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save.json")
STATIC_DIR = os.path.dirname(__file__)

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
}


class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, format, *args):
        msg = format % args if args else format
        print(f"[{self.log_date_time_string()}] {msg}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            self._handle_save_get()
        elif path == "/api/stage-progress":
            self._handle_progress_get()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if path == "/api/save":
            self._handle_save_post(data)
        elif path == "/api/stage-progress":
            self._handle_progress_post(data)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_save_get(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._send_json(200, data)
        else:
            self._send_json(200, {})

    def _handle_save_post(self, data):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._send_json(200, {"ok": True})

    def _handle_progress_get(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._send_json(200, data.get("stage_progress", {}))
        else:
            self._send_json(200, {})

    def _handle_progress_post(self, data):
        save_data = {}
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                save_data = json.load(f)
        save_data["stage_progress"] = data
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        self._send_json(200, {"ok": True})

    def guess_type(self, path):
        _, ext = os.path.splitext(path)
        return MIME_TYPES.get(ext, "application/octet-stream")


def main():
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), GameHandler) as httpd:
        print(f"提瓦特放置 Web 服务器已启动")
        print(f"本地访问: http://localhost:{PORT}")
        print(f"局域网访问: http://0.0.0.0:{PORT}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    main()