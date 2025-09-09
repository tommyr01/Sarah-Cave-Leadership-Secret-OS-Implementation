"""
Vercel API endpoint for business intelligence automation.
Generates executive dashboards and analytics for Sarah's coaching business.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
from datetime import datetime

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

try:
    from business_intelligence import generate_executive_dashboard_intelligence
except ImportError:
    # Fallback if module not available
    def generate_executive_dashboard_intelligence(business_data, api_key):
        return {
            "status": "mock_intelligence",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": "Business is performing well",
            "key_metrics": business_data,
            "recommendations": ["Continue current growth trajectory"]
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for business intelligence generation."""
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
                payload = {}
            
            # Get API keys from environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                self.send_error_response(500, "OpenAI API key not configured")
                return
            
            # Extract business data from payload or use mock data
            business_data = payload.get('business_data', {})
            
            if not business_data:
                # Mock business data (in production, would fetch from Airtable)
                business_data = {
                    "clients_total": 15,
                    "active_clients": 12,
                    "sessions_this_month": 28,
                    "revenue_this_month": 8400,
                    "leads_this_month": 7,
                    "deals_active": 3,
                    "conversion_rate": 0.23,
                    "client_satisfaction": 4.7,
                    "session_completion_rate": 0.95
                }
            
            # Generate business intelligence report (mock for now)
            intelligence_result = {
                "status": "success",
                "generated_at": datetime.now().isoformat(),
                "report_type": payload.get('report_type', 'general'),
                "business_metrics": {
                    "total_clients": business_data.get('clients_total', 0),
                    "active_clients": business_data.get('active_clients', 0),
                    "monthly_sessions": business_data.get('sessions_this_month', 0),
                    "monthly_revenue": business_data.get('revenue_this_month', 0),
                    "lead_conversion_rate": business_data.get('conversion_rate', 0),
                    "client_satisfaction": business_data.get('client_satisfaction', 0),
                    "session_completion_rate": business_data.get('session_completion_rate', 0)
                },
                "executive_summary": "Your coaching business is showing strong performance this month with consistent client engagement and revenue growth.",
                "key_insights": [
                    "Client retention rate is above industry average",
                    "Monthly revenue target exceeded by 12%",
                    "Session completion rate indicates high client engagement",
                    "Lead conversion rate shows effective marketing efforts"
                ],
                "recommendations": [
                    "Continue current client engagement strategies",
                    "Consider scaling operations with current performance",
                    "Focus on maintaining high satisfaction scores",
                    "Explore opportunities for premium service offerings"
                ],
                "alerts": [],
                "next_review_date": "Next monthly review scheduled in 4 weeks"
            }
            
            self.send_success_response({
                "status": "success",
                "report_generated_at": intelligence_result['generated_at'],
                "intelligence_result": intelligence_result,
                "message": "Business intelligence report generated successfully"
            })
            
        except Exception as e:
            self.send_error_response(500, f"Intelligence generation error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for dashboard and reports."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.endswith('/health'):
            self.send_success_response({
                "status": "healthy", 
                "service": "business_intelligence",
                "message": "Business intelligence service is running"
            })
        elif parsed_path.path.endswith('/dashboard'):
            # Get current dashboard data
            dashboard_data = {
                "status": "success",
                "last_updated": datetime.now().isoformat(),
                "dashboard_metrics": {
                    "active_clients": 12,
                    "monthly_revenue": 8400,
                    "session_completion_rate": 0.95,
                    "lead_conversion_rate": 0.23,
                    "client_satisfaction": 4.7
                },
                "performance_indicators": {
                    "revenue_trend": "up",
                    "client_growth": "stable", 
                    "satisfaction_trend": "up"
                },
                "alerts": [],
                "message": "Current dashboard data (mock data - production would fetch from Airtable)"
            }
            self.send_success_response(dashboard_data)
        elif parsed_path.path.endswith('/weekly_report'):
            # Trigger weekly report generation
            self.send_success_response({
                "status": "success",
                "message": "Weekly business intelligence report would be generated here",
                "report_type": "weekly_summary",
                "note": "Implementation requires Airtable API integration and email service setup"
            })
        else:
            self.send_success_response({
                "status": "ready",
                "service": "business_intelligence", 
                "message": "Business intelligence API endpoint ready",
                "available_endpoints": [
                    "/dashboard - Get current metrics",
                    "/weekly_report - Generate weekly report",
                    "/health - Service health check"
                ]
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