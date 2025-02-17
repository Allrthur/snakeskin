import os
import http.server
import socketserver
import json
from urllib.parse import urlparse
from datetime import datetime
import uuid
from pathlib import Path
import argparse
import traceback
import sys
from utils import absolute_path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    return parser.parse_args()

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    
    def __get_configs(self)->dict:
        config = {}
        
        # Parse request-types.json
        with open(absolute_path("configs/request-types.json"), mode="r") as file:
            request_types:dict = json.loads(file.read())
        request_types = {format_: type_ for type_, formats_ in request_types.items() for format_ in formats_}
        config["request-types"]=request_types
        
        # Return parsed config files
        return config
    
    def do_GET(self):
        # TODO: Get this bit of code to run only once
        configs = self.__get_configs()
        # TODO: Routing should be handled by other files
        routing_list = {"/index.html":"index.html"}
        
        # Parse the URL path
        parsed_path = urlparse(self.path).geturl()
        # Redirects
        if parsed_path=="/": # Redirect to landing page
            parsed_path="index.html"
            resolved_path = absolute_path("pages/").joinpath(parsed_path)
            content_type="text/html"
        elif parsed_path in routing_list: # It is a recognized routed page
            parsed_path=routing_list[parsed_path]
            resolved_path = absolute_path("pages/").joinpath(parsed_path)
            content_type="text/html"
        elif parsed_path=="/favicon.ico": # Redirect favicon to resources folder
            parsed_path = parsed_path[1:].replace(".ico",".png")
            resolved_path = absolute_path("resources/").joinpath(parsed_path)
            content_type="image/png"
        # All other content is handled by request-types.json
        else: 
            # Figure out request type from extension
            request_extension = parsed_path.split(".")[-1]
            if request_extension in configs["request-types"]:
                request_type = configs["request-types"][request_extension]
            else: # If request type is unsupported default to text
                request_type = "text"
            print("request-type: ", request_type)
        
            parsed_path=parsed_path[1:]
            resolved_path=parsed_path
            content_type=f"{request_type}/{parsed_path.split(".")[-1]}"
        
        print("parsed_path:\t", parsed_path)
        print("resolved_path:\t",resolved_path)
        try:
            with open(resolved_path, mode='rb') as file:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except:
            self.send_response(404, "Content not found for url")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<b>404: NOTHING TO SEE HERE, YET")
            

if __name__ == '__main__':
    args = get_args()
    PORT = args.port
    with socketserver.TCPServer(('', PORT), ServerHandler) as httpd:
        print(f"Mock server running on port {PORT}")
        try:httpd.serve_forever()
        except KeyboardInterrupt:print("Shutting down...")
        except:traceback.print_exception(*sys.exc_info())
        finally:httpd.server_close()