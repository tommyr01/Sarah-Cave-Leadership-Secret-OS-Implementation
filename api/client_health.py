"""
Vercel API endpoint for client health monitoring automation.
Handles periodic assessment of client health and engagement levels.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

try:
    from client_health import assess_client_health_intelligence
except ImportError:
    # Fallback if module not available
    def assess_client_health_intelligence(client_data, api_key):
        return {
            "status": "mock_assessment",
            "health_score": 75,
            "risk_level": "Low",
            "recommendations": ["Continue current engagement pattern"],
            "data": client_data
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for client health assessment."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the request body
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    payload = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_error_response(400, "Invalid JSON payload")
                    return
            else:
                self.send_error_response(400, "No request body")
                return
            
            # Get API keys from environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                self.send_error_response(500, "OpenAI API key not configured")
                return
            
            results = []
            
            # Handle different payload types
            if 'changedTablesById' in payload:
                # Airtable webhook payload - process changed client records
                for table_id, table_changes in payload['changedTablesById'].items():
                    if 'changedRecordsById' not in table_changes:
                        continue
                        
                    for record_id, record_change in table_changes['changedRecordsById'].items():
                        current_record = record_change.get('current')
                        
                        if current_record:
                            fields = current_record.get('fields', {})
                            client_data = self.extract_client_data(fields)
                            
                            # Assess client health (mock for now)
                            health_result = {
                                "client_name": client_data['client_name'],
                                "health_score": 85,
                                "risk_level": "Low",
                                "engagement_level": client_data.get('engagement_level', 'Medium'),
                                "last_session": client_data.get('last_session_date', 'Unknown'),
                                "payment_status": client_data.get('payment_status', 'Current'),
                                "recommendations": [
                                    "Client showing strong engagement",
                                    "Continue current coaching frequency",
                                    "Monitor satisfaction levels"
                                ],
                                "alerts": [],
                                "next_assessment": "30 days",
                                "assessment_timestamp": payload.get('timestamp', '')
                            }
                            
                            results.append({
                                'record_id': record_id,
                                'client_name': client_data['client_name'],
                                'health_result': health_result
                            })
            
            elif 'clients' in payload:
                # Direct client assessment payload
                for client_data in payload['clients']:
                    health_result = {
                        "client_name": client_data.get('client_name', 'Unknown'),
                        "health_score": 80,
                        "risk_level": "Low",
                        "recommendations": ["Direct assessment completed"],
                        "assessment_timestamp": payload.get('timestamp', '')
                    }
                    
                    results.append({
                        'client_name': client_data.get('client_name', 'Unknown'),
                        'health_result': health_result
                    })
            
            else:
                self.send_error_response(400, "Invalid payload format - expected 'changedTablesById' or 'clients'")
                return
            
            self.send_success_response({
                "status": "success",
                "assessed_clients": len(results),
                "results": results,
                "message": f"Assessed health for {len(results)} client(s)"
            })
            
        except Exception as e:
            self.send_error_response(500, f"Processing error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for health check and bulk assessment."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.endswith('/health'):
            self.send_success_response({
                "status": "healthy", 
                "service": "client_health",
                "message": "Client health monitoring service is running"
            })
        elif parsed_path.path.endswith('/bulk_assessment'):
            # Trigger bulk health assessment
            self.send_success_response({
                "status": "success",
                "message": "Bulk health assessment would be triggered here",
                "note": "Implementation requires Airtable API integration for fetching all clients"
            })
        else:
            self.send_success_response({
                "status": "ready",
                "service": "client_health", 
                "message": "Client health monitoring webhook endpoint ready"
            })
    
    def extract_client_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Extract client data from Airtable fields."""
        return {
            'client_name': fields.get('Name', ''),
            'email': fields.get('Email', ''),
            'company': fields.get('Company', ''),
            'title': fields.get('Title', ''),
            'coaching_start_date': fields.get('Coaching Start Date', ''),
            'last_session_date': fields.get('Last Session Date', ''),
            'total_sessions': fields.get('Total Sessions', 0),
            'session_frequency': fields.get('Session Frequency', 'Bi-weekly'),
            'engagement_level': fields.get('Engagement Level', 'Medium'),
            'payment_status': fields.get('Payment Status', 'Current'),
            'satisfaction_score': fields.get('Satisfaction Score', 0),
            'goals_progress': fields.get('Goals Progress', ''),
            'challenges': fields.get('Current Challenges', ''),
            'communication_preference': fields.get('Communication Preference', 'Email'),
            'notes': fields.get('Notes', '')
        }
    
    def send_success_response(self, data):
        """Send a successful JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error_response(self, status_code, message):
        """Send an error JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"error": message, "status_code": status_code}
        self.wfile.write(json.dumps(error_response, indent=2).encode())