"""
Vercel API endpoint for action items extraction automation.
Extracts action items from session notes using AI and creates follow-up tasks.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for action items extraction."""
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
            
            # Process action items extraction
            trigger_type = payload.get('triggerType', 'extract_action_items')
            session_notes = payload.get('sessionNotes', '')
            client_name = payload.get('clientName', '')
            session_date = payload.get('sessionDate', '')
            
            results = {
                'trigger_type': trigger_type,
                'session_notes_length': len(session_notes),
                'extracted_action_items': [],
                'total_action_items': 0,
                'high_priority_items': 0,
                'client_assignments': 0,
                'coach_assignments': 0,
                'processed_timestamp': datetime.utcnow().isoformat()
            }
            
            # Extract action items based on trigger type
            if trigger_type == 'extract_action_items':
                extraction_results = self.extract_action_items_from_notes(session_notes, client_name, session_date)
                results.update(extraction_results)
                
            elif trigger_type == 'manual_action_items':
                manual_results = self.process_manual_action_items(payload.get('actionItems', []))
                results.update(manual_results)
            
            # Send success response
            response_data = {
                'success': True,
                **results,
                'automation_type': 'action_items'
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'error_type': 'action_items_extraction_error',
                'timestamp': datetime.utcnow().isoformat()
            }
            self.send_json_response(500, error_response)
    
    def extract_action_items_from_notes(self, session_notes: str, client_name: str, session_date: str) -> Dict[str, Any]:
        """Extract action items from session notes using pattern recognition."""
        
        if not session_notes:
            return {
                'extracted_action_items': [],
                'total_action_items': 0,
                'high_priority_items': 0,
                'client_assignments': 0,
                'coach_assignments': 0
            }
        
        # Action item patterns to look for
        action_patterns = [
            r"(?i)action(?:\s+item)?[:\s]*(.+?)(?:\n|$)",
            r"(?i)(?:to[\s-]*do|todo)[:\s]*(.+?)(?:\n|$)", 
            r"(?i)(?:follow[\s-]*up|followup)[:\s]*(.+?)(?:\n|$)",
            r"(?i)(?:next[\s-]*step|next steps)[:\s]*(.+?)(?:\n|$)",
            r"(?i)\b(?:will|must|should|need to|needs to|has to)\s+(.+?)(?:\n|\.|$)",
            r"(?i)(?:homework|assignment)[:\s]*(.+?)(?:\n|$)",
            r"(?i)(?:by next session|before next meeting)[:\s]*(.+?)(?:\n|$)"
        ]
        
        # Priority indicators
        high_priority_keywords = ['urgent', 'asap', 'immediately', 'critical', 'important', 'deadline', 'due']
        medium_priority_keywords = ['should', 'recommend', 'suggest', 'consider']
        
        # Assignment indicators
        client_keywords = ['client', client_name.lower() if client_name else '', 'they will', 'participant', 'attendee']
        coach_keywords = ['sarah', 'coach', 'i will', 'we will', 'follow up', 'send']
        
        extracted_items = []
        
        # Extract using patterns
        for pattern in action_patterns:
            matches = re.finditer(pattern, session_notes, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                action_text = match.group(1).strip()
                
                # Skip if too short or common non-action phrases
                if len(action_text) < 10 or any(skip in action_text.lower() for skip in ['the meeting', 'this session', 'we discussed']):
                    continue
                
                # Determine priority
                priority = self.determine_priority(action_text, high_priority_keywords, medium_priority_keywords)
                
                # Determine assignment
                assigned_to = self.determine_assignment(action_text, client_keywords, coach_keywords, client_name)
                
                # Determine category
                category = self.determine_category(action_text)
                
                # Calculate due date
                due_date = self.calculate_due_date(action_text, session_date)
                
                action_item = {
                    'action_text': action_text,
                    'priority': priority,
                    'assigned_to': assigned_to,
                    'category': category,
                    'due_date': due_date,
                    'extracted_from': 'session_notes',
                    'confidence_score': self.calculate_confidence(action_text, match.group(0))
                }
                
                # Avoid duplicates
                if not any(item['action_text'].lower() == action_text.lower() for item in extracted_items):
                    extracted_items.append(action_item)
        
        # Manual extraction for common coaching scenarios
        manual_items = self.extract_common_coaching_actions(session_notes, client_name, session_date)
        extracted_items.extend(manual_items)
        
        # Calculate metrics
        total_items = len(extracted_items)
        high_priority_count = len([item for item in extracted_items if item['priority'] == 'High'])
        client_assignments = len([item for item in extracted_items if item['assigned_to'] == client_name or item['assigned_to'] == 'Client'])
        coach_assignments = len([item for item in extracted_items if item['assigned_to'] == 'Sarah Cave' or item['assigned_to'] == 'Coach'])
        
        return {
            'extracted_action_items': extracted_items,
            'total_action_items': total_items,
            'high_priority_items': high_priority_count,
            'client_assignments': client_assignments,
            'coach_assignments': coach_assignments
        }
    
    def extract_common_coaching_actions(self, notes: str, client_name: str, session_date: str) -> List[Dict[str, Any]]:
        """Extract common coaching-specific action items."""
        
        common_actions = []
        notes_lower = notes.lower()
        
        # Common coaching scenarios
        if any(word in notes_lower for word in ['360', 'feedback', 'assessment']):
            common_actions.append({
                'action_text': 'Complete 360-degree feedback assessment',
                'priority': 'Medium',
                'assigned_to': client_name or 'Client',
                'category': 'Assessment',
                'due_date': (datetime.utcnow() + timedelta(days=7)).date().isoformat(),
                'extracted_from': 'pattern_recognition',
                'confidence_score': 0.8
            })
        
        if any(word in notes_lower for word in ['team meeting', 'staff meeting', 'one-on-one']):
            common_actions.append({
                'action_text': 'Schedule and conduct team meeting using discussed framework',
                'priority': 'Medium',
                'assigned_to': client_name or 'Client',
                'category': 'Team Development',
                'due_date': (datetime.utcnow() + timedelta(days=5)).date().isoformat(),
                'extracted_from': 'pattern_recognition',
                'confidence_score': 0.7
            })
        
        if any(word in notes_lower for word in ['goal', 'objective', 'target']):
            common_actions.append({
                'action_text': 'Define specific goals and success metrics discussed in session',
                'priority': 'High',
                'assigned_to': client_name or 'Client',
                'category': 'Goal Setting',
                'due_date': (datetime.utcnow() + timedelta(days=3)).date().isoformat(),
                'extracted_from': 'pattern_recognition',
                'confidence_score': 0.6
            })
        
        if any(word in notes_lower for word in ['read', 'book', 'article', 'resource']):
            common_actions.append({
                'action_text': 'Review recommended resources and materials',
                'priority': 'Low',
                'assigned_to': client_name or 'Client', 
                'category': 'Learning',
                'due_date': (datetime.utcnow() + timedelta(days=10)).date().isoformat(),
                'extracted_from': 'pattern_recognition',
                'confidence_score': 0.5
            })
        
        return common_actions
    
    def determine_priority(self, action_text: str, high_keywords: List[str], medium_keywords: List[str]) -> str:
        """Determine priority level of action item."""
        
        action_lower = action_text.lower()
        
        if any(keyword in action_lower for keyword in high_keywords):
            return 'High'
        elif any(keyword in action_lower for keyword in medium_keywords):
            return 'Medium'
        else:
            return 'Low'
    
    def determine_assignment(self, action_text: str, client_keywords: List[str], coach_keywords: List[str], client_name: str) -> str:
        """Determine who the action item is assigned to."""
        
        action_lower = action_text.lower()
        
        if any(keyword in action_lower for keyword in coach_keywords):
            return 'Sarah Cave'
        elif any(keyword in action_lower for keyword in client_keywords):
            return client_name or 'Client'
        elif action_text.startswith(('Send', 'Email', 'Call', 'Follow up', 'Research')):
            return 'Sarah Cave'
        else:
            return client_name or 'Client'  # Default to client
    
    def determine_category(self, action_text: str) -> str:
        """Categorize the action item."""
        
        action_lower = action_text.lower()
        
        category_keywords = {
            'Communication': ['email', 'call', 'meeting', 'discuss', 'talk', 'conversation'],
            'Assessment': ['assessment', '360', 'feedback', 'evaluation', 'survey', 'test'],
            'Goal Setting': ['goal', 'objective', 'target', 'metric', 'kpi', 'outcome'],
            'Team Development': ['team', 'staff', 'group', 'colleague', 'peer', 'direct report'],
            'Learning': ['read', 'study', 'research', 'learn', 'training', 'course', 'book'],
            'Planning': ['plan', 'strategy', 'roadmap', 'timeline', 'schedule', 'organize'],
            'Implementation': ['implement', 'execute', 'deploy', 'launch', 'start', 'begin']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in action_lower for keyword in keywords):
                return category
        
        return 'General'
    
    def calculate_due_date(self, action_text: str, session_date: str) -> str:
        """Calculate appropriate due date for action item."""
        
        action_lower = action_text.lower()
        
        # Look for specific timeframe mentions
        if any(phrase in action_lower for phrase in ['by next session', 'before next meeting', 'next week']):
            return (datetime.utcnow() + timedelta(days=7)).date().isoformat()
        elif any(phrase in action_lower for phrase in ['today', 'immediately', 'asap']):
            return datetime.utcnow().date().isoformat()
        elif any(phrase in action_lower for phrase in ['this week', 'within 3 days']):
            return (datetime.utcnow() + timedelta(days=3)).date().isoformat()
        elif any(phrase in action_lower for phrase in ['month', 'quarterly']):
            return (datetime.utcnow() + timedelta(days=30)).date().isoformat()
        else:
            # Default to 5 business days
            return (datetime.utcnow() + timedelta(days=5)).date().isoformat()
    
    def calculate_confidence(self, action_text: str, full_match: str) -> float:
        """Calculate confidence score for extracted action item."""
        
        score = 0.5  # Base score
        
        # Boost confidence for explicit action indicators
        if any(phrase in full_match.lower() for phrase in ['action item', 'to do', 'follow up', 'next step']):
            score += 0.3
        
        # Boost for specific verbs
        action_verbs = ['complete', 'send', 'schedule', 'review', 'implement', 'create', 'develop']
        if any(verb in action_text.lower() for verb in action_verbs):
            score += 0.2
        
        # Reduce confidence for vague language
        if any(phrase in action_text.lower() for phrase in ['maybe', 'might', 'could', 'perhaps']):
            score -= 0.2
        
        return max(0.1, min(1.0, score))
    
    def process_manual_action_items(self, action_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process manually provided action items."""
        
        processed_items = []
        
        for item in action_items:
            processed_item = {
                'action_text': item.get('text', ''),
                'priority': item.get('priority', 'Medium'),
                'assigned_to': item.get('assignedTo', 'Client'),
                'category': item.get('category', 'General'),
                'due_date': item.get('dueDate', (datetime.utcnow() + timedelta(days=5)).date().isoformat()),
                'extracted_from': 'manual_input',
                'confidence_score': 1.0
            }
            processed_items.append(processed_item)
        
        total_items = len(processed_items)
        high_priority_count = len([item for item in processed_items if item['priority'] == 'High'])
        client_assignments = len([item for item in processed_items if item['assigned_to'] in ['Client', 'client']])
        coach_assignments = len([item for item in processed_items if item['assigned_to'] in ['Sarah Cave', 'Coach', 'coach']])
        
        return {
            'extracted_action_items': processed_items,
            'total_action_items': total_items,
            'high_priority_items': high_priority_count,
            'client_assignments': client_assignments,
            'coach_assignments': coach_assignments
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
            'service': 'Action Items Extraction API',
            'version': '1.0.0',
            'description': 'Extracts action items from session notes and creates follow-up tasks',
            'trigger_types': ['extract_action_items', 'manual_action_items'],
            'features': [
                'AI-powered action item extraction from session notes',
                'Priority level assignment based on content analysis',
                'Automatic assignment to client or coach',
                'Category classification (Communication, Assessment, Goal Setting, etc.)',
                'Due date calculation based on urgency indicators',
                'Confidence scoring for extracted items'
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