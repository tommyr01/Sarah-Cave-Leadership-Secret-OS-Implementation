"""
Main API health check endpoint for Sarah Cave Leadership OS
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "sarah_cave_leadership_os", 
            "message": "All automation services are operational",
            "endpoints": [
                "/api/webhook",
                "/api/lead_scoring", 
                "/api/session_processing",
                "/api/client_health",
                "/api/business_intelligence"
            ]
        }
        
        self.wfile.write(json.dumps(response).encode())
        return