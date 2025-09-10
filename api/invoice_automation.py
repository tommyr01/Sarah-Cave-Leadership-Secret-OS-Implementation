"""
Vercel API endpoint for invoice automation.
Handles automatic invoice generation, payment tracking, and financial workflows.
"""

import json
from datetime import datetime, timedelta
import uuid

def handler(request):
    """Handle requests for invoice automation."""
    
    # Handle OPTIONS for CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    # Handle GET requests
    if request.method == 'GET':
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(info_data, indent=2)
        }
    
    # Handle POST requests
    if request.method == 'POST':
        try:
            # Parse request body
            if hasattr(request, 'get_json'):
                payload = request.get_json() or {}
            else:
                import json
                payload = json.loads(request.body) if request.body else {}
            
            # Process invoice automation
            trigger_type = payload.get('automationType', payload.get('triggerType', 'invoice_automation'))
            session_data = payload.get('recordData', payload.get('sessionData', {}))
            
            # Generate invoice results
            invoice_results = process_invoice_generation(trigger_type, session_data)
            
            # Send success response
            response_data = {
                'success': True,
                'automation_type': 'invoice_automation',
                **invoice_results
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_data, indent=2)
            }
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'invoice_automation_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(error_response, indent=2)
            }
    
    # Method not allowed
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Method not allowed'})
    }


def process_invoice_generation(trigger_type, session_data):
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
    invoice_number = generate_invoice_number()
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


def generate_invoice_number():
    """Generate a unique invoice number."""
    date_prefix = datetime.utcnow().strftime('%Y%m')
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"INV-{date_prefix}-{random_suffix}"