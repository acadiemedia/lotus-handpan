#!/usr/bin/env python3
import sys, functools, http.server, socketserver, os, json

ROOT = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(ROOT, "piano_calibration.json")

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/calibration":
            if os.path.exists(CALIBRATION_FILE):
                try:
                    with open(CALIBRATION_FILE, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception:
                    pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            resp = b"{}"
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/save_calibration":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                parsed = json.loads(body.decode("utf-8"))
                with open(CALIBRATION_FILE, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)
                resp = json.dumps({"status": "ok", "saved": True}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return
            except Exception as e:
                err = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
                return
        self.send_response(404)
        self.end_headers()

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(H, directory=ROOT)
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print("serving %s on 0.0.0.0:%d (no-cache)" % (ROOT, port), flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    main()
