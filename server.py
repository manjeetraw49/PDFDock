# -*- coding: utf-8 -*-
"""
PDFDock Local Development and Production Web Server
Features:
- Multi-threaded socketserver for rapid concurrent file serving
- Proper MIME types, CORS headers, and UTF-8 encoding
- 100% Client-Side Privacy Document Processing
"""

import http.server
import socketserver
import os
import sys

class PDFDockHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run(port=8080):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ("127.0.0.1", port)
    with socketserver.ThreadingTCPServer(server_address, PDFDockHTTPRequestHandler) as httpd:
        print("============================================================")
        print(f"PDFDock Web Server running at: http://localhost:{port}")
        print(f"Directory:                    {os.path.dirname(os.path.abspath(__file__))}")
        print("============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
