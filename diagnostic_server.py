#!/usr/bin/env python3
"""
Component test server to diagnose MCP server issues
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import traceback

class DiagnosticHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'python_version': sys.version,
                'environment': {
                    'AZURE_DEVOPS_ORG': os.getenv('AZURE_DEVOPS_ORG', 'not_set'),
                    'PORT': os.getenv('PORT', 'not_set')
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/test-imports':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            imports = {}
            
            # Test basic imports
            try:
                import mcp
                imports['mcp'] = {'status': 'success', 'version': getattr(mcp, '__version__', 'unknown')}
            except Exception as e:
                imports['mcp'] = {'status': 'failed', 'error': str(e)}
                
            try:
                import uvicorn
                imports['uvicorn'] = {'status': 'success', 'version': getattr(uvicorn, '__version__', 'unknown')}
            except Exception as e:
                imports['uvicorn'] = {'status': 'failed', 'error': str(e)}
                
            try:
                from azure_devops_mcp.main import main
                imports['azure_devops_mcp'] = {'status': 'success'}
            except Exception as e:
                imports['azure_devops_mcp'] = {'status': 'failed', 'error': str(e), 'traceback': traceback.format_exc()}
                
            try:
                from mcp.server import FastMCP
                imports['FastMCP'] = {'status': 'success'}
            except Exception as e:
                imports['FastMCP'] = {'status': 'failed', 'error': str(e)}
                
            response = {'imports': imports}
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/test-mcp-init':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                from mcp.server import FastMCP
                mcp_server = FastMCP("Test Server")
                response = {'status': 'success', 'message': 'FastMCP initialized successfully'}
            except Exception as e:
                response = {'status': 'failed', 'error': str(e), 'traceback': traceback.format_exc()}
                
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found - Available: /health, /test-imports, /test-mcp-init')
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def main():
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), DiagnosticHandler)
    print(f"Diagnostic server starting on 0.0.0.0:{port}")
    print("Available endpoints:")
    print("  /health - Health check")
    print("  /test-imports - Test module imports")
    print("  /test-mcp-init - Test MCP initialization")
    server.serve_forever()

if __name__ == "__main__":
    main()