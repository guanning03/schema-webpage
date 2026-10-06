#!/usr/bin/env python3
"""Local-only static preview, with byte ranges for seekable gameplay videos."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import re


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def send_head(self):
        self.byte_range = None
        path = Path(self.translate_path(self.path))
        if any(part.startswith('.') for part in path.relative_to(Path(self.directory)).parts):
            self.send_error(404)
            return None
        if path.is_dir() and not (path / 'index.html').exists():
            self.send_error(404)
            return None
        requested = self.headers.get('Range')
        if not requested or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested)
        if not match or not any(match.groups()):
            self.send_error(400, 'Invalid byte range')
            return None
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start >= size or start > end:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        self.byte_range = (start, end)
        return path.open('rb')

    def copyfile(self, source, outputfile):
        try:
            if self.byte_range is None:
                return super().copyfile(source, outputfile)
            start, end = self.byte_range
            source.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    directory = str(Path(__file__).resolve().parent)
    handler = partial(PreviewHandler, directory=directory)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    print(f'Schema preview: http://localhost:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
