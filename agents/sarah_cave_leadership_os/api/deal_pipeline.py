"""
Vercel API endpoint for deal pipeline automation.
Handles deal stage progression, probability updates, and pipeline intelligence.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
from datetime import datetime, timedelta

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for deal pipeline automation."""
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
            
            # Process the deal pipeline automation
            results = []
            processed_deals = 0
            
            # Extract deal data from payload
            if 'changedTablesById' in payload:
                deals_table = payload['changedTablesById'].get('tblDeals', {})
                changed_records = deals_table.get('changedRecordsById', {})
                
                for record_id, record_data in changed_records.items():
                    if 'current' in record_data and 'fields' in record_data['current']:
                        deal_fields = record_data['current']['fields']
                        
                        # Process this deal
                        pipeline_result = self.process_deal_pipeline(deal_fields)
                        
                        results.append({
                            'record_id': record_id,
                            'deal_name': deal_fields.get('Deal Name', 'Unknown Deal'),
                            'pipeline_result': pipeline_result
                        })
                        processed_deals += 1
            
            # Send success response
            response_data = {
                'success': True,
                'processed_deals': processed_deals,
                'results': results,
                'timestamp': datetime.utcnow().isoformat(),
                'automation_type': 'deal_pipeline'
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'pipeline_processing_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def process_deal_pipeline(self, deal_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Process deal pipeline logic and return recommendations."""
        
        # Extract key fields
        current_stage = deal_fields.get('Stage', '')
        current_probability = deal_fields.get('Probability', 0)
        deal_value = deal_fields.get('Deal Value', 0)
        
        # BANT criteria
        budget_confirmed = deal_fields.get('Budget Confirmed', False)
        authority_confirmed = deal_fields.get('Authority Confirmed', False) 
        need_identified = deal_fields.get('Need Identified', False)
        timeline_established = deal_fields.get('Timeline Established', False)
        
        # Timeline data
        days_in_stage = deal_fields.get('Days in Stage', 0)
        expected_close = deal_fields.get('Expected Close Date', '')
        
        # Calculate updated probability based on BANT criteria
        updated_probability = self.calculate_probability(
            current_stage, budget_confirmed, authority_confirmed, 
            need_identified, timeline_established, days_in_stage
        )
        
        # Determine recommended next stage
        recommended_stage = self.get_recommended_stage(
            current_stage, budget_confirmed, authority_confirmed,
            need_identified, timeline_established
        )
        
        # Generate smart next action
        next_action = self.generate_next_action(
            current_stage, deal_fields.get('Deal Name', 'Deal'),
            budget_confirmed, authority_confirmed, need_identified, timeline_established
        )
        
        # Calculate follow-up date
        follow_up_date = self.calculate_follow_up_date(current_stage, days_in_stage)
        
        # Generate alerts for stalled deals or issues
        alerts = self.generate_pipeline_alerts(
            current_stage, days_in_stage, updated_probability,
            budget_confirmed, authority_confirmed, need_identified, timeline_established
        )
        
        return {
            'updated_probability': updated_probability,
            'recommended_stage': recommended_stage,
            'next_action': next_action,
            'follow_up_date': follow_up_date,
            'alerts': alerts,
            'bant_score': self.calculate_bant_score(budget_confirmed, authority_confirmed, need_identified, timeline_established),
            'stage_velocity_days': days_in_stage,
            'processed_timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_probability(self, stage: str, budget: bool, authority: bool, need: bool, timeline: bool, days_in_stage: int) -> int:
        """Calculate deal probability based on stage and BANT criteria."""
        
        # Base probability by stage
        stage_probabilities = {
            'Lead': 10,
            'Qualified': 25,
            'Proposal': 50,
            'Negotiation': 75,
            'Closed Won': 100,
            'Closed Lost': 0
        }
        
        base_prob = stage_probabilities.get(stage, 20)
        
        # BANT multiplier (max 25% boost)
        bant_count = sum([budget, authority, need, timeline])
        bant_multiplier = 1 + (bant_count * 0.0625)  # 6.25% per BANT criteria
        
        # Time decay (reduce probability if stalled too long)
        if days_in_stage > 30:
            time_penalty = min(0.2, (days_in_stage - 30) * 0.01)  # Max 20% penalty
            bant_multiplier -= time_penalty
        
        final_prob = int(base_prob * bant_multiplier)
        return max(0, min(100, final_prob))
    
    def get_recommended_stage(self, current_stage: str, budget: bool, authority: bool, need: bool, timeline: bool) -> str:
        """Recommend next stage based on BANT completion."""
        
        bant_count = sum([budget, authority, need, timeline])
        
        if current_stage == 'Lead' and bant_count >= 2:
            return 'Qualified'
        elif current_stage == 'Qualified' and bant_count >= 3:
            return 'Proposal'
        elif current_stage == 'Proposal' and bant_count == 4:
            return 'Negotiation'
        elif current_stage == 'Negotiation' and bant_count == 4:
            return 'Ready to Close'
        else:
            return current_stage  # Stay in current stage
    
    def generate_next_action(self, stage: str, deal_name: str, budget: bool, authority: bool, need: bool, timeline: bool) -> str:
        """Generate specific next action based on deal context."""
        
        missing_bant = []
        if not budget: missing_bant.append('Budget')
        if not authority: missing_bant.append('Authority')
        if not need: missing_bant.append('Need')
        if not timeline: missing_bant.append('Timeline')
        
        if stage == 'Lead':
            if missing_bant:
                return f"Qualify {deal_name}: Confirm {', '.join(missing_bant[:2])} with discovery call"
            else:
                return f"Move {deal_name} to Qualified stage - all BANT criteria met"
        
        elif stage == 'Qualified':
            if missing_bant:
                return f"Complete qualification: Validate {', '.join(missing_bant)} before proposal"
            else:
                return f"Prepare and send proposal for {deal_name}"
        
        elif stage == 'Proposal':
            return f"Follow up on {deal_name} proposal - schedule decision call within 3 days"
        
        elif stage == 'Negotiation':
            return f"Finalize terms for {deal_name} - send contract for signature"
        
        else:
            return f"Review {deal_name} status and update next steps"
    
    def calculate_follow_up_date(self, stage: str, days_in_stage: int) -> str:
        """Calculate appropriate follow-up date based on stage and velocity."""
        
        now = datetime.utcnow()
        
        # Urgent follow-up for stalled deals
        if days_in_stage > 14:
            follow_up = now + timedelta(days=1)
        elif stage in ['Proposal', 'Negotiation']:
            follow_up = now + timedelta(days=2)
        elif stage in ['Qualified']:
            follow_up = now + timedelta(days=5)
        else:  # Lead stage
            follow_up = now + timedelta(days=7)
        
        return follow_up.strftime('%Y-%m-%d')
    
    def generate_pipeline_alerts(self, stage: str, days_in_stage: int, probability: int, budget: bool, authority: bool, need: bool, timeline: bool) -> list:
        """Generate alerts for deals requiring attention."""
        
        alerts = []
        
        # Stalled deal alerts
        if days_in_stage > 30:
            alerts.append(f"Deal stalled in {stage} for {days_in_stage} days - needs immediate attention")
        elif days_in_stage > 14 and stage in ['Proposal', 'Negotiation']:
            alerts.append(f"High-value stage stalled for {days_in_stage} days - follow up urgently")
        
        # BANT completion alerts
        missing_bant = sum([not budget, not authority, not need, not timeline])
        if missing_bant > 2 and stage != 'Lead':
            alerts.append(f"Missing {missing_bant} BANT criteria - may not be qualified")
        
        # Probability alerts
        if probability < 30 and stage in ['Qualified', 'Proposal']:
            alerts.append("Low probability for stage - consider moving to nurture")
        
        # Expected close date alerts (would need actual date comparison)
        # This would require parsing the expected close date
        
        return alerts
    
    def calculate_bant_score(self, budget: bool, authority: bool, need: bool, timeline: bool) -> int:
        """Calculate BANT completeness score out of 100."""
        return int(sum([budget, authority, need, timeline]) * 25)
    
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
            'service': 'Deal Pipeline Automation API',
            'version': '1.0.0',
            'description': 'Handles deal stage progression and pipeline intelligence',
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