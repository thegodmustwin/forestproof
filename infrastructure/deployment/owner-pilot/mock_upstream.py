"""CI-only loopback upstream for the owner gateway; never runs on the VPS."""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def reply(self):
        authorization_absent = self.headers.get("Authorization") is None
        subject_matches = self.headers.get_all("X-Forestproof-Owner-Subject") == [os.environ["FORESTPROOF_OWNER_SUBJECT"]]
        token_matches = self.headers.get_all("X-Forestproof-Owner-Gateway-Token") == [os.environ["FORESTPROOF_OWNER_GATEWAY_TOKEN"]]
        body = b"identity verified" if authorization_absent and subject_matches and token_matches else b"invalid gateway assertion"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply()

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.reply()

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 13000), Handler).serve_forever()
