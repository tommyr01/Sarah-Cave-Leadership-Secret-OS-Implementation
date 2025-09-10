"""
Vercel API endpoint for follow-ups and reminders automation.
Handles automated reminders for leads, action items, payments, and session scheduling.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for follow-ups automation."""
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
            
            # Process follow-ups automation
            trigger_type = payload.get('triggerType', 'scheduled')
            reminder_types = payload.get('reminderTypes', ['lead_followup', 'action_items', 'payment_reminders', 'session_scheduling'])
            
            results = {
                'lead_followups_processed': 0,
                'action_reminders_sent': 0, 
                'payment_reminders_sent': 0,
                'session_reminders_sent': 0,
                'total_overdue_items': 0,
                'total_notifications_sent': 0,
                'reminders_generated': [],
                'processed_timestamp': datetime.utcnow().isoformat()
            }
            
            # Process each reminder type
            if 'lead_followup' in reminder_types:
                lead_results = self.process_lead_followups()
                results['lead_followups_processed'] = lead_results['processed']
                results['reminders_generated'].extend(lead_results['reminders'])
                results['total_notifications_sent'] += lead_results['notifications_sent']
            
            if 'action_items' in reminder_types:
                action_results = self.process_action_item_reminders()
                results['action_reminders_sent'] = action_results['processed']
                results['reminders_generated'].extend(action_results['reminders'])
                results['total_notifications_sent'] += action_results['notifications_sent']
            
            if 'payment_reminders' in reminder_types:
                payment_results = self.process_payment_reminders()
                results['payment_reminders_sent'] = payment_results['processed']
                results['reminders_generated'].extend(payment_results['reminders'])
                results['total_notifications_sent'] += payment_results['notifications_sent']
            
            if 'session_scheduling' in reminder_types:
                session_results = self.process_session_reminders()
                results['session_reminders_sent'] = session_results['processed']
                results['reminders_generated'].extend(session_results['reminders'])
                results['total_notifications_sent'] += session_results['notifications_sent']
            
            # Calculate total overdue items
            results['total_overdue_items'] = sum([
                results['lead_followups_processed'],
                results['action_reminders_sent'],
                results['payment_reminders_sent']
            ])
            
            # Send success response
            response_data = {
                'success': True,
                'trigger_type': trigger_type,
                **results,
                'automation_type': 'follow_ups'
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'followup_processing_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def process_lead_followups(self) -> Dict[str, Any]:
        """Process overdue lead follow-ups."""
        
        # Mock data - in real implementation, would query Airtable for overdue leads
        today = datetime.utcnow().date()
        
        # Simulate finding overdue leads
        overdue_leads = [
            {
                'name': 'John Smith - TechCorp',
                'days_overdue': 3,
                'next_action': 'Send follow-up email with case study',
                'priority': 'Hot',
                'lead_source': 'LinkedIn'
            },
            {
                'name': 'Sarah Johnson - FinanceFlow', 
                'days_overdue': 7,
                'next_action': 'Schedule discovery call',
                'priority': 'Warm',
                'lead_source': 'Referral'
            }
        ]
        
        reminders = []
        notifications_sent = 0
        
        for lead in overdue_leads:
            reminder = {
                'type': 'lead_followup',
                'recipient': 'Sarah Cave',
                'subject': f"Overdue Lead Follow-up: {lead['name']}",
                'message': f"Lead {lead['name']} is {lead['days_overdue']} days overdue for follow-up. Next action: {lead['next_action']}",
                'priority': lead['priority'],
                'due_date': (datetime.utcnow() - timedelta(days=lead['days_overdue'])).isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(reminder)
            notifications_sent += 1
        
        return {
            'processed': len(overdue_leads),
            'reminders': reminders,
            'notifications_sent': notifications_sent
        }
    
    def process_action_item_reminders(self) -> Dict[str, Any]:
        """Process overdue action item reminders."""
        
        today = datetime.utcnow().date()
        
        # Simulate finding overdue action items
        overdue_actions = [
            {
                'client_name': 'Mike Wilson',
                'action_item': 'Complete 360 feedback survey',
                'days_overdue': 2,
                'priority': 'High',
                'session_date': '2024-01-15'
            },
            {
                'client_name': 'Lisa Chen',
                'action_item': 'Schedule team meeting using new framework',
                'days_overdue': 5,
                'priority': 'Medium',
                'session_date': '2024-01-10'
            }
        ]
        
        reminders = []
        notifications_sent = 0
        
        for action in overdue_actions:
            # Reminder to Sarah
            sarah_reminder = {
                'type': 'action_item_reminder',
                'recipient': 'Sarah Cave',
                'subject': f"Client Action Item Overdue: {action['client_name']}",
                'message': f"Action item '{action['action_item']}' for {action['client_name']} is {action['days_overdue']} days overdue.",
                'priority': action['priority'],
                'client': action['client_name'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(sarah_reminder)
            notifications_sent += 1
            
            # Reminder to client (would need client email)
            client_reminder = {
                'type': 'action_item_reminder',
                'recipient': action['client_name'],
                'subject': f"Action Item Reminder: {action['action_item']}",
                'message': f"This is a friendly reminder about your action item: '{action['action_item']}' from our session on {action['session_date']}.",
                'priority': action['priority'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(client_reminder)
            notifications_sent += 1
        
        return {
            'processed': len(overdue_actions),
            'reminders': reminders,
            'notifications_sent': notifications_sent
        }
    
    def process_payment_reminders(self) -> Dict[str, Any]:
        """Process overdue payment reminders."""
        
        today = datetime.utcnow().date()
        
        # Simulate finding overdue payments
        overdue_payments = [
            {
                'client_name': 'Corporate Solutions Inc',
                'invoice_number': 'INV-2024-001',
                'amount': 15000,
                'days_overdue': 5,
                'payment_terms': 'Net 30'
            }
        ]
        
        reminders = []
        notifications_sent = 0
        
        for payment in overdue_payments:
            # Reminder to Sarah
            sarah_reminder = {
                'type': 'payment_reminder',
                'recipient': 'Sarah Cave',
                'subject': f"Overdue Payment: {payment['invoice_number']}",
                'message': f"Invoice {payment['invoice_number']} for {payment['client_name']} (${payment['amount']:,}) is {payment['days_overdue']} days overdue.",
                'amount': payment['amount'],
                'days_overdue': payment['days_overdue'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(sarah_reminder)
            notifications_sent += 1
            
            # Reminder to client
            client_reminder = {
                'type': 'payment_reminder',
                'recipient': payment['client_name'],
                'subject': f"Payment Reminder: Invoice {payment['invoice_number']}",
                'message': f"Your invoice {payment['invoice_number']} for ${payment['amount']:,} is now {payment['days_overdue']} days past due. Please remit payment at your earliest convenience.",
                'amount': payment['amount'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(client_reminder)
            notifications_sent += 1
        
        return {
            'processed': len(overdue_payments),
            'reminders': reminders,
            'notifications_sent': notifications_sent
        }
    
    def process_session_reminders(self) -> Dict[str, Any]:
        """Process upcoming session reminders."""
        
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        
        # Simulate finding sessions tomorrow
        upcoming_sessions = [
            {
                'client_name': 'David Rodriguez',
                'session_date': tomorrow.isoformat(),
                'session_time': '10:00 AM EST',
                'session_type': 'Regular Coaching',
                'format': 'Video',
                'pre_work': 'Review leadership assessment results'
            },
            {
                'client_name': 'Jennifer Kim',
                'session_date': tomorrow.isoformat(),
                'session_time': '2:00 PM EST',
                'session_type': 'Check-in',
                'format': 'Phone',
                'pre_work': None
            }
        ]
        
        reminders = []
        notifications_sent = 0
        
        for session in upcoming_sessions:
            # Reminder to Sarah
            sarah_reminder = {
                'type': 'session_reminder',
                'recipient': 'Sarah Cave',
                'subject': f"Session Tomorrow: {session['client_name']}",
                'message': f"Session with {session['client_name']} tomorrow at {session['session_time']} ({session['session_type']}, {session['format']}).",
                'session_date': session['session_date'],
                'session_time': session['session_time'],
                'client': session['client_name'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(sarah_reminder)
            notifications_sent += 1
            
            # Reminder to client
            pre_work_msg = f" Please complete: {session['pre_work']}" if session['pre_work'] else ""
            client_reminder = {
                'type': 'session_reminder',
                'recipient': session['client_name'],
                'subject': f"Coaching Session Reminder - Tomorrow at {session['session_time']}",
                'message': f"This is a reminder of your {session['session_type']} session tomorrow at {session['session_time']}.{pre_work_msg}",
                'session_date': session['session_date'],
                'session_time': session['session_time'],
                'created_at': datetime.utcnow().isoformat()
            }
            reminders.append(client_reminder)
            notifications_sent += 1
        
        return {
            'processed': len(upcoming_sessions),
            'reminders': reminders,
            'notifications_sent': notifications_sent
        }
    
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
            'service': 'Follow-ups & Reminders Automation API',
            'version': '1.0.0',
            'description': 'Handles automated reminders for leads, action items, payments, and sessions',
            'reminder_types': ['lead_followup', 'action_items', 'payment_reminders', 'session_scheduling'],
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