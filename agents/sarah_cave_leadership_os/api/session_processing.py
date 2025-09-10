"""
Vercel API endpoint for session processing automation.
Handles Airtable webhooks for coaching session updates and processes notes using AI.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

try:
    from session_processing import process_session_intelligence
except ImportError:
    # Fallback if module not available
    async def process_session_intelligence(session_data, api_key):
        return {"status": "mock_processing", "data": session_data}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for session processing."""
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
            
            # Validate webhook structure
            if 'changedTablesById' not in payload:
                self.send_success_response({
                    "status": "ignored", 
                    "reason": "No changed tables in payload"
                })
                return
            
            results = []
            
            # Process each changed table
            for table_id, table_changes in payload['changedTablesById'].items():
                if 'changedRecordsById' not in table_changes:
                    continue
                    
                # Process each changed record
                for record_id, record_change in table_changes['changedRecordsById'].items():
                    current_record = record_change.get('current')
                    
                    # Only process sessions with raw notes that need processing
                    if current_record:
                        fields = current_record.get('fields', {})
                        
                        # Check if session has raw notes but no processed summary
                        raw_notes = fields.get('Raw Notes', '')
                        processed_summary = fields.get('Session Summary', '')
                        
                        if raw_notes and not processed_summary:
                            # Extract session data
                            session_data = {
                                'client_name': fields.get('Client Name', ''),
                                'session_date': fields.get('Session Date', ''),
                                'session_type': fields.get('Session Type', 'Leadership Coaching'),
                                'duration': fields.get('Duration (minutes)', 60),
                                'raw_notes': raw_notes,
                                'session_objectives': fields.get('Session Objectives', ''),
                                'client_context': fields.get('Client Context', ''),
                                'previous_action_items': fields.get('Previous Action Items', ''),
                                'coaching_focus_areas': fields.get('Coaching Focus Areas', [])
                            }
                            
                            # For now, return the session data for processing
                            # AI processing would happen here
                            processing_result = {
                                "status": "ready_for_processing",
                                "session_summary": f"Session with {session_data['client_name']} on {session_data['session_date']}",
                                "key_insights": ["Session notes received and ready for AI processing"],
                                "action_items": ["Set up AI processing integration"],
                                "follow_up_tasks": ["Configure OpenAI integration"],
                                "client_progress": "Session data captured successfully"
                            }
                            
                            results.append({
                                'record_id': record_id,
                                'client_name': session_data['client_name'],
                                'processing_result': processing_result
                            })
            
            self.send_success_response({
                "status": "success",
                "processed_sessions": len(results),
                "results": results,
                "message": f"Processed {len(results)} session(s) successfully"
            })
            
        except Exception as e:
            self.send_error_response(500, f"Processing error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for health check."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.endswith('/health'):
            self.send_success_response({
                "status": "healthy", 
                "service": "session_processing",
                "message": "Session processing service is running"
            })
        else:
            self.send_success_response({
                "status": "ready",
                "service": "session_processing", 
                "message": "Session processing webhook endpoint ready"
            })
    
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