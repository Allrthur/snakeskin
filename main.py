import os
import http.server
import socketserver
import json
from urllib.parse import urlparse
from datetime import datetime
import uuid
from pathlib import Path
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int)
    return parser.parse_args()

def absolute_path(path:str):
    return Path(__file__).parent.joinpath(path)

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path).geturl()
        if parsed_path=="/": parsed_path="index.html"
        elif parsed_path.startswith("/"): parsed_path=parsed_path[1:]
        resolved_path = absolute_path("pages/").joinpath(parsed_path)
        print(resolved_path)
        print(parsed_path)
        try:
            with open(resolved_path, mode='rb') as file:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        except:
            self.send_response(404, "No such page in the pages folder")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<b>404: NOTHING TO SEE HERE, YET")
            

if __name__ == '__main__':
    args = get_args()
    PORT = args.port
    with socketserver.TCPServer(('', PORT), ServerHandler) as httpd:
        print(f"Mock server running on port {PORT}")
        httpd.serve_forever()
    # parsed_path="index.html"
    # resolved_path = absolute_path("pages/").joinpath(parsed_path)
    # print(resolved_path)
    