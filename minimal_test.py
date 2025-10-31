#!/usr/bin/env python3
"""
Minimal Python test to verify basic functionality
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MinimalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'python_working',
            'python_version': sys.version,
            'platform': sys.platform,
            'path': sys.path[:3],  # First 3 entries only
            'env_vars': {
                'PORT': os.getenv('PORT', 'not_set'),
                'AZURE_DEVOPS_ORG': os.getenv('AZURE_DEVOPS_ORG', 'not_set'),
                'PYTHONPATH': os.getenv('PYTHONPATH', 'not_set')
            },
            'cwd': os.getcwd(),
            'files': os.listdir('.')[:10]  # First 10 files only
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        print(f"[HTTP] {format % args}")

def main():
    port = int(os.getenv('PORT', 8000))
    print(f"Starting minimal Python server on port {port}")
    print(f"Python version: {sys.version}")
    
    try:
        server = HTTPServer(('0.0.0.0', port), MinimalHandler)
        print("Server starting...")
        server.serve_forever()
    except Exception as e:
        print(f"Server failed: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()