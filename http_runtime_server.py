#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple

from http_runtime_entry_mock import handle_http_runtime_request


class RuntimeHandler(BaseHTTPRequestHandler):
    server_version = 'xinbi-runtime-http/0.1'

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Tuple[dict | None, str | None]:
        length = int(self.headers.get('Content-Length', '0') or '0')
        raw = self.rfile.read(length) if length > 0 else b''
        if not raw:
            return None, 'empty_body'
        try:
            return json.loads(raw.decode('utf-8')), None
        except json.JSONDecodeError:
            return None, 'invalid_json'

    def do_POST(self):
        if self.path != '/runtime':
            self._send_json(404, {'ok': False, 'error': 'NOT_FOUND', 'message': 'route not found'})
            return

        body, err = self._read_json_body()
        if err == 'empty_body':
            self._send_json(400, {'ok': False, 'error': 'INVALID_INPUT', 'message': 'empty request body'})
            return
        if err == 'invalid_json':
            self._send_json(400, {'ok': False, 'error': 'PARSE_ERROR', 'message': 'invalid json body'})
            return

        headers = {
            'X-Request-Id': self.headers.get('X-Request-Id'),
            'X-Trace-Id': self.headers.get('X-Trace-Id'),
        }
        result = handle_http_runtime_request(body=body, headers=headers)
        status = 200 if result.get('ok') else 400
        self._send_json(status, result)

    def log_message(self, format, *args):
        return


def run_server(host: str = '0.0.0.0', port: int = 8787):
    server = ThreadingHTTPServer((host, port), RuntimeHandler)
    print(f'http runtime server listening on http://{host}:{port}/runtime')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    import os
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8787'))
    run_server(host=host, port=port)
