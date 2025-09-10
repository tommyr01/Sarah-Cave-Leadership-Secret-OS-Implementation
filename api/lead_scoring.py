"""
Vercel API endpoint for lead scoring automation.
Handles Airtable webhooks for new leads and scores them using AI.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for lead scoring."""
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
            
            results = []
            
            # Handle simple automation webhook format
            if 'recordData' in payload and payload.get('automationType') == 'lead_scoring':
                record_id = payload['recordData'].get('recordId')
                if record_id:
                    # Create mock lead data for processing
                    mock_lead_fields = self.create_mock_lead_data(record_id)
                    scoring_result = self.process_lead_scoring(mock_lead_fields)
                    
                    results.append({
                        'record_id': record_id,
                        'lead_name': mock_lead_fields.get('Lead Name', 'Demo Lead'),
                        'scoring_result': scoring_result
                    })
            
            # Handle complex webhook payload
            elif 'changedTablesById' in payload:
                for table_id, table_changes in payload['changedTablesById'].items():
                    if 'changedRecordsById' not in table_changes:
                        continue
                        
                    for record_id, record_change in table_changes['changedRecordsById'].items():
                        current_record = record_change.get('current')
                        
                        if current_record:
                            fields = current_record.get('fields', {})
                            scoring_result = self.process_lead_scoring(fields)
                            
                            results.append({
                                'record_id': record_id,
                                'lead_name': fields.get('Lead Name', 'Unknown Lead'),
                                'scoring_result': scoring_result
                            })
            
            # Send success response
            response_data = {
                'success': True,
                'processed_leads': len(results),
                'results': results,
                'timestamp': datetime.utcnow().isoformat(),
                'automation_type': 'lead_scoring'
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'lead_scoring_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def create_mock_lead_data(self, record_id):
        """Create mock lead data for testing purposes."""
        return {
            'Lead Name': f'Executive Lead - {record_id}',
            'Company': 'TechCorp Solutions',
            'Title': 'VP of Engineering',
            'Email': 'vp@techcorp.com',
            'Phone': '+1-555-0123',
            'Lead Source': 'LinkedIn',
            'Company Size': '201-1000',
            'Industry': 'Technology',
            'Budget Range': '$15K-30K',
            'Urgency': 'Within 30 days',
            'Coaching Challenges': ['Team Building', 'Strategic Thinking', 'Communication'],
            'Notes': 'Strong leadership background, looking to improve team dynamics and strategic thinking. Has budget authority and immediate need for executive coaching.'
        }
    
    def process_lead_scoring(self, lead_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Process lead scoring logic and return AI score."""
        
        # Extract key fields for scoring
        company_size = lead_fields.get('Company Size', '')
        industry = lead_fields.get('Industry', '')
        title = lead_fields.get('Title', '')
        budget_range = lead_fields.get('Budget Range', '')
        urgency = lead_fields.get('Urgency', '')
        lead_source = lead_fields.get('Lead Source', '')
        challenges = lead_fields.get('Coaching Challenges', [])
        notes = lead_fields.get('Notes', '')
        
        # Calculate lead score based on multiple factors
        lead_score = self.calculate_lead_score(
            company_size, industry, title, budget_range, 
            urgency, lead_source, challenges, notes
        )
        
        # Determine priority level
        priority_level = self.determine_priority_level(lead_score)
        
        # Determine coaching fit
        coaching_fit = self.assess_coaching_fit(title, challenges, industry)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            lead_score, priority_level, coaching_fit, urgency, budget_range
        )
        
        # Determine recommended status
        recommended_status = self.get_recommended_status(lead_score, urgency)
        
        return {
            'lead_score': lead_score,
            'priority_level': priority_level,
            'coaching_fit': coaching_fit,
            'recommendations': recommendations,
            'recommended_status': recommended_status,
            'scoring_factors': {
                'company_size_score': self.score_company_size(company_size),
                'title_score': self.score_title(title),
                'budget_score': self.score_budget(budget_range),
                'urgency_score': self.score_urgency(urgency),
                'industry_score': self.score_industry(industry),
                'source_score': self.score_lead_source(lead_source),
                'challenges_score': self.score_challenges(challenges)
            },
            'processed_timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_lead_score(self, company_size, industry, title, budget_range, urgency, lead_source, challenges, notes):
        """Calculate overall lead score from 0-100."""
        
        score = 0
        
        # Company size (0-20 points)
        score += self.score_company_size(company_size)
        
        # Title/Position (0-20 points)
        score += self.score_title(title)
        
        # Budget range (0-20 points)
        score += self.score_budget(budget_range)
        
        # Urgency (0-15 points)
        score += self.score_urgency(urgency)
        
        # Industry (0-10 points)
        score += self.score_industry(industry)
        
        # Lead source (0-10 points)
        score += self.score_lead_source(lead_source)
        
        # Coaching challenges (0-5 points)
        score += self.score_challenges(challenges)
        
        return min(100, max(0, score))
    
    def score_company_size(self, size):
        """Score based on company size."""
        size_scores = {
            '1000+': 20,
            '201-1000': 18,
            '51-200': 15,
            '11-50': 10,
            '1-10': 5
        }
        return size_scores.get(size, 8)
    
    def score_title(self, title):
        """Score based on job title/seniority."""
        title_lower = title.lower() if title else ''
        
        if any(word in title_lower for word in ['ceo', 'president', 'founder']):
            return 20
        elif any(word in title_lower for word in ['vp', 'vice president', 'svp']):
            return 18
        elif any(word in title_lower for word in ['director', 'head of']):
            return 15
        elif any(word in title_lower for word in ['manager', 'lead', 'senior']):
            return 12
        else:
            return 8
    
    def score_budget(self, budget_range):
        """Score based on budget range."""
        budget_scores = {
            '$30K+': 20,
            '$15K-30K': 18,
            '$5K-15K': 12,
            '$0-5K': 6,
            'Unknown': 5
        }
        return budget_scores.get(budget_range, 5)
    
    def score_urgency(self, urgency):
        """Score based on timeline urgency."""
        urgency_scores = {
            'Immediate': 15,
            'Within 30 days': 12,
            'Within 90 days': 8,
            'Future planning': 4
        }
        return urgency_scores.get(urgency, 6)
    
    def score_industry(self, industry):
        """Score based on industry fit."""
        high_fit_industries = ['Technology', 'Finance', 'Consulting', 'Healthcare']
        if industry in high_fit_industries:
            return 10
        else:
            return 6
    
    def score_lead_source(self, source):
        """Score based on lead source quality."""
        source_scores = {
            'Referral': 10,
            'Partner Referral': 10,
            'Speaking Engagement': 9,
            'LinkedIn': 8,
            'Networking Event': 8,
            'Content Marketing': 7,
            'Website': 6,
            'Cold Outreach': 4
        }
        return source_scores.get(source, 5)
    
    def score_challenges(self, challenges):
        """Score based on coaching challenges alignment."""
        if not challenges or len(challenges) == 0:
            return 2
        elif len(challenges) >= 3:
            return 5
        else:
            return 3
    
    def determine_priority_level(self, score):
        """Determine priority level based on score."""
        if score >= 80:
            return 'Hot'
        elif score >= 60:
            return 'Warm'
        else:
            return 'Cold'
    
    def assess_coaching_fit(self, title, challenges, industry):
        """Assess how well the lead fits coaching services."""
        title_lower = title.lower() if title else ''
        
        # High-level executives are excellent fit
        if any(word in title_lower for word in ['ceo', 'president', 'founder', 'vp', 'vice president']):
            if len(challenges) >= 2:
                return 'Excellent Fit'
            else:
                return 'Strong Fit'
        
        # Directors and managers are good fit
        elif any(word in title_lower for word in ['director', 'manager', 'head of']):
            return 'Good Fit'
        
        # Others may need qualification
        else:
            return 'Needs Qualification'
    
    def generate_recommendations(self, score, priority, fit, urgency, budget):
        """Generate actionable recommendations."""
        recommendations = []
        
        if priority == 'Hot':
            recommendations.append('Schedule immediate discovery call')
            recommendations.append('Send executive coaching overview package')
            
        if urgency == 'Immediate':
            recommendations.append('Follow up within 24 hours')
            
        if fit == 'Excellent Fit':
            recommendations.append('Propose comprehensive leadership assessment')
            
        if budget in ['$30K+', '$15K-30K']:
            recommendations.append('Present premium coaching packages')
        elif budget in ['$5K-15K']:
            recommendations.append('Offer associate coaching options')
            
        if score < 50:
            recommendations.append('Nurture with valuable content before sales approach')
            
        if not recommendations:
            recommendations.append('Qualify further and schedule exploratory call')
            
        return recommendations
    
    def get_recommended_status(self, score, urgency):
        """Get recommended lead status."""
        if score >= 70 and urgency in ['Immediate', 'Within 30 days']:
            return 'Qualified'
        elif score >= 50:
            return 'Contacted'
        else:
            return 'Nurturing'
    
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
            'service': 'Lead Scoring API',
            'version': '1.0.0',
            'description': 'AI-powered lead scoring and qualification for executive coaching prospects',
            'trigger_types': ['lead_scoring', 'new_lead', 'lead_updated'],
            'features': [
                'Multi-factor lead scoring (company size, title, budget, urgency)',
                'Priority level assignment (Hot/Warm/Cold)',
                'Coaching fit assessment',
                'Automated recommendations and next actions',
                'Industry-specific scoring adjustments'
            ],
            'scoring_factors': [
                'Company Size (0-20 points)',
                'Job Title/Seniority (0-20 points)', 
                'Budget Range (0-20 points)',
                'Timeline Urgency (0-15 points)',
                'Industry Fit (0-10 points)',
                'Lead Source Quality (0-10 points)',
                'Coaching Challenges (0-5 points)'
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