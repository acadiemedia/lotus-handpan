#!/usr/bin/env python3
import sys, functools, http.server, socketserver, os

ROOT = os.path.dirname(os.path.abspath(__file__))

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(H, directory=ROOT)
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print("serving %s on 0.0.0.0:%d (no-cache)" % (ROOT, port), flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    main()
