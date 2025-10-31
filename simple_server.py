#!/usr/bin/env python3
"""
Simple test server to verify Azure Web App deployment
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'python_version': os.sys.version,
                'environment': {
                    'AZURE_DEVOPS_ORG': os.getenv('AZURE_DEVOPS_ORG', 'not_set'),
                    'PORT': os.getenv('PORT', 'not_set')
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def main():
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Simple test server starting on 0.0.0.0:{port}")
    print("Available endpoints:")
    print("  /health - Health check endpoint")
    server.serve_forever()

if __name__ == "__main__":
    main()