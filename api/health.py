"""
System health check endpoint
"""

from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check environment variables
        env_status = {}
        required_vars = ['OPENAI_API_KEY', 'AIRTABLE_API_KEY', 'AIRTABLE_BASE_ID']
        
        for var in required_vars:
            env_status[var] = "configured" if os.getenv(var) else "missing"
        
        response = {
            "status": "healthy",
            "service": "sarah_cave_leadership_os",
            "environment": env_status,
            "endpoints": {
                "webhook": "/api/webhook",
                "lead_scoring": "/api/lead_scoring", 
                "session_processing": "/api/session_processing",
                "client_health": "/api/client_health",
                "business_intelligence": "/api/business_intelligence"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response, indent=2).encode())
        return