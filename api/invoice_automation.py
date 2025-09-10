"""
Vercel API endpoint for invoice automation.
Handles automatic invoice generation, payment tracking, and financial workflows.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
import uuid

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for invoice automation."""
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
            
            # Process invoice automation
            trigger_type = payload.get('automationType', 'invoice_automation')
            session_data = payload.get('recordData', {})
            
            # Generate invoice results
            invoice_results = self.process_invoice_generation(trigger_type, session_data)
            
            # Send success response
            response_data = {
                'success': True,
                'automation_type': 'invoice_automation',
                **invoice_results
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'invoice_automation_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def process_invoice_generation(self, trigger_type, session_data):
        """Process invoice generation based on trigger type."""
        
        session_id = session_data.get('sessionId', session_data.get('recordId', ''))
        client_id = session_data.get('clientId', '')
        
        # Mock session data - in real implementation, would fetch from Airtable
        session_info = {
            'session_id': session_id,
            'client_name': 'TechCorp Solutions',
            'client_id': client_id,
            'session_type': 'Executive Coaching',
            'duration': '90 mins',
            'session_date': datetime.utcnow().date().isoformat(),
            'rate': 500,  # per session
            'associate_rate': 150,  # if associate delivered
            'package_type': 'Executive 1:1 - 6 months'
        }
        
        # Generate invoice
        invoice_number = self.generate_invoice_number()
        invoice_amount = session_info['rate']
        
        generated_invoice = {
            'invoice_number': invoice_number,
            'client_name': session_info['client_name'],
            'client_id': session_info['client_id'],
            'amount': invoice_amount,
            'session_ids': [session_id],
            'invoice_date': datetime.utcnow().date().isoformat(),
            'due_date': (datetime.utcnow().date() + timedelta(days=30)).isoformat(),
            'payment_terms': 'Net 30',
            'status': 'Draft',
            'description': f"{session_info['session_type']} - {session_info['duration']} session on {session_info['session_date']}",
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Calculate commission if associate delivered
        commission_amount = 0
        if session_info.get('associate_rate'):
            commission_amount = session_info['associate_rate']
        
        return {
            'trigger_type': trigger_type,
            'invoices_generated': 1,
            'total_invoice_amount': invoice_amount,
            'commission_calculated': commission_amount,
            'generated_invoices': [generated_invoice],
            'payment_reminders_sent': 0,
            'payments_processed': 0,
            'payment_updates': [],
            'processed_timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        date_prefix = datetime.utcnow().strftime('%Y%m')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{date_prefix}-{random_suffix}"
    
    def send_json_response(self, status_code, data):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response."""
        error_data = {
            'success': False,
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.send_json_response(status_code, error_data)
    
    def do_GET(self):
        """Handle GET requests - return API information."""
        info_data = {
            'service': 'Invoice Automation API',
            'version': '1.0.0',
            'description': 'Handles automatic invoice generation, payment tracking, and financial workflows',
            'trigger_types': ['invoice_automation', 'session_completed', 'manual_invoice', 'payment_update'],
            'features': [
                'Automatic invoice generation from completed sessions',
                'Manual invoice creation for multiple sessions', 
                'Payment tracking and overdue reminders',
                'Commission calculations for associates',
                'Financial reporting integration'
            ],
            'methods': ['POST', 'GET'],
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.send_json_response(200, info_data)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()