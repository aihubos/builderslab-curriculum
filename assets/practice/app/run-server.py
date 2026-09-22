"""Local-only practice server. Run with Python 3; stop with Ctrl+C."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 8765), partial(SimpleHTTPRequestHandler, directory=str(root)))
    except OSError as exc:
        raise SystemExit(f'Cannot start port 8765. Keep existing programs running and ask your instructor. {exc}')
    print('Open http://127.0.0.1:8765/output/ after creating output/index.html. Stop: Ctrl+C')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()
