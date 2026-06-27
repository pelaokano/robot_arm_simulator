"""
server.py — HTTP server para el simulador de brazo robot.
Usa HTTP polling en lugar de WebSocket (compatible con VPN y firewall).
Requiere: solo biblioteca estándar de Python (sin dependencias externas)
"""

import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

_queue: deque = deque(maxlen=500)  # mensajes pendientes
_seq   = 0                          # número de secuencia
_current: dict = {"type": "idle", "seq": 0}  # último mensaje
_connected = threading.Event()
_server: HTTPServer = None


class _Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silenciar logs de HTTP

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self._serve_html()
        elif self.path.startswith('/state'):
            self._serve_state()
        else:
            self.send_error(404)

    def _serve_html(self):
        html = (Path(__file__).parent / "robot_simulator.html").read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def _serve_state(self):
        global _current
        _connected.set()
        # Si hay mensajes en cola, servir el siguiente
        if _queue:
            msg = _queue.popleft()
        else:
            msg = _current

        data = json.dumps(msg).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()


def _run():
    global _server
    _server = HTTPServer(('127.0.0.1', 8080), _Handler)
    _server.serve_forever()


def start():
    """Lanza servidor HTTP en background. Retorna inmediatamente."""
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    # Esperar brevemente a que el socket esté listo
    import time; time.sleep(0.3)
    print("[server] http://127.0.0.1:8080")


def wait_for_browser(timeout=30):
    """Bloquea hasta que el browser haga su primera petición."""
    return _connected.wait(timeout=timeout)


def send(msg: dict):
    """Encola un mensaje para el browser."""
    global _seq, _current
    _seq += 1
    msg['seq'] = _seq
    _current = msg
    _queue.append(msg)
