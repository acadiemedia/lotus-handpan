#!/usr/bin/env python3
import sys, functools, http.server, socketserver, os, json, urllib.parse, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(ROOT, "piano_calibration.json")
SCORES_DIR = os.path.join(ROOT, "scores")
AUDIO_DIR = os.path.join(SCORES_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Lazy import transcribe_handpan
def get_transcriber():
    import transcribe_handpan
    return transcribe_handpan

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/calibration":
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

        elif path == "/api/audio":
            vid = query.get("id", [None])[0]
            if not vid or not all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in vid):
                self.send_error(400, "Invalid video ID")
                return
            try:
                wav_path = os.path.join(AUDIO_DIR, f"{vid}.wav")
                if not os.path.exists(wav_path):
                    tb = get_transcriber()
                    _, wav_path = tb.extract_audio(vid)

                if os.path.exists(wav_path):
                    file_size = os.path.getsize(wav_path)
                    range_header = self.headers.get("Range")
                    if range_header and range_header.startswith("bytes="):
                        ranges = range_header[6:].split("-")
                        start = int(ranges[0]) if ranges[0] else 0
                        end = int(ranges[1]) if ranges[1] else file_size - 1
                        length = end - start + 1

                        self.send_response(206)
                        self.send_header("Content-Type", "audio/wav")
                        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                        self.send_header("Content-Length", str(length))
                        self.send_header("Accept-Ranges", "bytes")
                        self.end_headers()

                        with open(wav_path, "rb") as f:
                            f.seek(start)
                            self.wfile.write(f.read(length))
                        return
                    else:
                        self.send_response(200)
                        self.send_header("Content-Type", "audio/wav")
                        self.send_header("Content-Length", str(file_size))
                        self.send_header("Accept-Ranges", "bytes")
                        self.end_headers()

                        with open(wav_path, "rb") as f:
                            self.wfile.write(f.read())
                        return
                else:
                    self.send_error(404, "Audio not found")
                    return
            except Exception as e:
                self.send_error(500, str(e))
                return

        elif path == "/api/auto_populate":
            vid = query.get("id", [None])[0]
            if not vid or not all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in vid):
                self.send_error(400, "Invalid video ID")
                return
            try:
                start_sec = int(query.get("start", [0])[0])
            except (ValueError, TypeError):
                start_sec = 0
            try:
                duration = int(query.get("dur", [90])[0])
            except (ValueError, TypeError):
                duration = 90

            try:
                cache_key = f"{vid}_{start_sec}_{duration}" if start_sec > 0 else vid
                score_json = os.path.join(SCORES_DIR, f"{cache_key}.json")
                if os.path.exists(score_json):
                    with open(score_json, "r", encoding="utf-8") as f:
                        score_data = json.load(f)
                    layout = score_data.get("layout", [])
                    notes = score_data.get("notes", [])
                else:
                    tb = get_transcriber()
                    _, wav_path = tb.extract_audio(vid, start_sec=start_sec, duration=duration)
                    notes, layout = tb.transcribe_audio(wav_path)
                    score_data = {
                        "videoId": vid,
                        "startSec": start_sec,
                        "duration": duration,
                        "layout": layout,
                        "notes": notes,
                        "totalNotes": len(notes),
                        "generatedAt": int(os.path.getmtime(wav_path))
                    }
                    with open(score_json, "w", encoding="utf-8") as f:
                        json.dump(score_data, f, indent=2)

                resp = json.dumps({
                    "status": "ok",
                    "videoId": vid,
                    "startSec": start_sec,
                    "duration": duration,
                    "layout": layout,
                    "totalNotes": len(notes)
                }).encode("utf-8")
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

class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = functools.partial(H, directory=ROOT)
    with ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
        print("serving %s on 0.0.0.0:%d (threading, no-cache)" % (ROOT, port), flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    main()
