"""
Vercel API endpoint for invoice automation.
Handles automatic invoice generation, payment tracking, and financial workflows.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List
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
            trigger_type = payload.get('triggerType', 'session_completed')
            session_data = payload.get('sessionData', {})
            
            results = {
                'trigger_type': trigger_type,
                'invoices_generated': 0,
                'total_invoice_amount': 0,
                'payment_reminders_sent': 0,
                'payments_processed': 0,
                'commission_calculated': 0,
                'generated_invoices': [],
                'payment_updates': [],
                'processed_timestamp': datetime.utcnow().isoformat()
            }
            
            # Process based on trigger type
            if trigger_type == 'session_completed':
                invoice_results = self.process_session_completion(session_data)
                results.update(invoice_results)
                
            elif trigger_type == 'manual_invoice':
                invoice_results = self.process_manual_invoice(session_data)
                results.update(invoice_results)
                
            elif trigger_type == 'payment_update':
                payment_results = self.process_payment_update(session_data)
                results.update(payment_results)
            
            # Send success response
            response_data = {
                'success': True,
                **results,
                'automation_type': 'invoice_automation'
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
    
    def process_session_completion(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice generation when a session is completed."""
        
        session_id = session_data.get('sessionId', '')
        client_id = session_data.get('clientId', '')
        
        # Mock session data - in real implementation, would fetch from Airtable
        session_info = {
            'session_id': session_id,
            'client_name': 'TechCorp Solutions',
            'client_id': client_id,
            'session_type': 'Executive Coaching',
            'duration': '90 mins',
            'session_date': '2024-01-15',
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
            'description': f\"{session_info['session_type']} - {session_info['duration']} session on {session_info['session_date']}\",
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Calculate commission if associate delivered
        commission_amount = 0
        if session_info.get('associate_rate'):
            commission_amount = session_info['associate_rate']
        
        return {
            'invoices_generated': 1,
            'total_invoice_amount': invoice_amount,
            'commission_calculated': commission_amount,
            'generated_invoices': [generated_invoice],
            'payment_reminders_sent': 0,
            'payments_processed': 0,
            'payment_updates': []
        }
    
    def process_manual_invoice(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process manual invoice generation for multiple sessions or custom amounts."""
        
        client_id = session_data.get('clientId', '')
        session_ids = session_data.get('sessionIds', [])
        manual_amount = session_data.get('invoiceAmount', 0)
        
        # Mock client data
        client_info = {
            'client_name': 'Enterprise Corp',
            'client_id': client_id,
            'payment_terms': 'Net 30',
            'package_type': 'Custom Package'
        }
        
        # Calculate invoice amount
        if manual_amount > 0:
            invoice_amount = manual_amount
            description = f"Custom coaching package - {len(session_ids)} sessions"
        else:
            # Calculate based on sessions (mock calculation)
            session_rate = 500
            invoice_amount = len(session_ids) * session_rate
            description = f"Coaching sessions - {len(session_ids)} sessions delivered"
        
        # Generate invoice
        invoice_number = self.generate_invoice_number()
        
        generated_invoice = {
            'invoice_number': invoice_number,
            'client_name': client_info['client_name'],
            'client_id': client_info['client_id'],
            'amount': invoice_amount,
            'session_ids': session_ids,
            'invoice_date': datetime.utcnow().date().isoformat(),
            'due_date': (datetime.utcnow().date() + timedelta(days=30)).isoformat(),
            'payment_terms': client_info['payment_terms'],
            'status': 'Sent',
            'description': description,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return {
            'invoices_generated': 1,
            'total_invoice_amount': invoice_amount,
            'commission_calculated': 0,
            'generated_invoices': [generated_invoice],
            'payment_reminders_sent': 0,
            'payments_processed': 0,
            'payment_updates': []
        }
    
    def process_payment_update(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment updates and status changes."""
        
        invoice_id = session_data.get('invoiceId', '')
        
        # Mock invoice data - would fetch from Airtable in real implementation
        invoice_info = {
            'invoice_id': invoice_id,
            'invoice_number': 'INV-2024-001',
            'client_name': 'Global Industries',
            'amount': 7500,
            'status': 'Sent',
            'days_outstanding': 35,
            'payment_terms': 'Net 30'
        }
        
        payment_updates = []
        payment_reminders_sent = 0
        payments_processed = 0
        
        # Check if payment is overdue
        if invoice_info['days_outstanding'] > 30 and invoice_info['status'] != 'Paid':
            # Send overdue payment reminder
            reminder = {
                'invoice_id': invoice_id,
                'invoice_number': invoice_info['invoice_number'],
                'client_name': invoice_info['client_name'],
                'amount': invoice_info['amount'],
                'days_overdue': invoice_info['days_outstanding'] - 30,
                'reminder_type': 'overdue_payment',
                'message': f"Invoice {invoice_info['invoice_number']} is {invoice_info['days_outstanding'] - 30} days overdue",
                'sent_at': datetime.utcnow().isoformat()
            }
            payment_updates.append(reminder)
            payment_reminders_sent = 1
        
        # Simulate payment processing (would integrate with Stripe/payment processor)
        if invoice_info['status'] == 'Sent':
            # Check for payments (mock)
            import random
            if random.random() > 0.7:  # 30% chance of payment
                payment_update = {
                    'invoice_id': invoice_id,
                    'invoice_number': invoice_info['invoice_number'],
                    'client_name': invoice_info['client_name'],
                    'amount': invoice_info['amount'],
                    'payment_method': 'ACH Transfer',
                    'payment_date': datetime.utcnow().date().isoformat(),
                    'status_update': 'Paid',
                    'processed_at': datetime.utcnow().isoformat()
                }
                payment_updates.append(payment_update)
                payments_processed = 1
        
        return {
            'invoices_generated': 0,
            'total_invoice_amount': 0,
            'commission_calculated': 0,
            'generated_invoices': [],
            'payment_reminders_sent': payment_reminders_sent,
            'payments_processed': payments_processed,
            'payment_updates': payment_updates
        }
    
    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        date_prefix = datetime.utcnow().strftime('%Y%m')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV-{date_prefix}-{random_suffix}"
    
    def calculate_invoice_totals(self, base_amount: float, tax_rate: float = 0.0, discount: float = 0.0) -> Dict[str, float]:
        """Calculate invoice totals including tax and discounts."""
        
        subtotal = base_amount - discount
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        return {
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'tax_amount': round(tax_amount, 2),
            'total': round(total, 2)
        }
    
    def determine_payment_terms(self, client_type: str, package_type: str) -> str:
        """Determine appropriate payment terms based on client and package."""
        
        if 'Custom' in package_type or client_type == 'Enterprise':
            return 'Net 30'
        elif 'Executive 1:1' in package_type:
            return '50% Upfront, 50% Mid-Program'
        else:
            return 'Due on Receipt'
    
    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
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
            'trigger_types': ['session_completed', 'manual_invoice', 'payment_update'],
            'features': [
                'Automatic invoice generation from completed sessions',
                'Manual invoice creation for multiple sessions',
                'Payment tracking and overdue reminders',
                'Commission calculations for associates',
                'Financial reporting integration'
            ],
            'methods': ['POST'],
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