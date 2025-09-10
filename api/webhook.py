"""
Main webhook endpoint for Airtable automation
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path to import automation modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get content length
            content_length = int(self.headers['Content-Length'])
            
            # Read the POST data
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            # Basic webhook validation
            if 'changedTablesById' not in payload:
                self.send_error_response(400, "Invalid webhook payload")
                return
            
            # TODO: Process webhook with automation modules
            # For now, return success
            response = {
                "status": "success",
                "message": "Webhook received and processed",
                "payload_keys": list(payload.keys())
            }
            
            self.send_success_response(response)
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON payload")
        except Exception as e:
            self.send_error_response(500, f"Processing error: {str(e)}")
    
    def do_GET(self):
        # Health check for webhook endpoint
        response = {
            "status": "healthy",
            "service": "webhook_processor",
            "message": "Webhook endpoint is operational"
        }
        self.send_success_response(response)
    
    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"error": message, "status": "error"}
        self.wfile.write(json.dumps(error_response).encode())