#!/usr/bin/env python3
"""Static server with HTTP Range support, for testing the site locally.

python -m http.server ignores Range headers, and Chrome seeks video with
Range requests, so under it the hero loop and the film's run order buttons
silently stall. Use this instead, then run audit.py against it:

    python _build/serve.py . 8899
"""
import os, sys, re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path) or "Range" not in self.headers:
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        size = os.fstat(f.fileno()).st_size
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers["Range"])
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, "Range not satisfiable")
            f.close()
            return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        f.seek(start)
        self._range_len = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        n = getattr(self, "_range_len", None)
        if n is None:
            return super().copyfile(source, outputfile)
        while n > 0:
            chunk = source.read(min(65536, n))
            if not chunk:
                break
            outputfile.write(chunk)
            n -= len(chunk)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.chdir(sys.argv[1])
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8899
    ThreadingHTTPServer(("127.0.0.1", port), RangeHandler).serve_forever()
