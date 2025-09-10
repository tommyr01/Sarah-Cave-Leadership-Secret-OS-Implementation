"""
AI-powered session note generation and action item extraction for Sarah Cave's Leadership Secret Operating System.
Automatically converts raw session notes into structured summaries with extracted action items and client health signals.
"""

from typing import Dict, Any, List, Optional, Tuple
import openai
import json
from datetime import datetime, timedelta
from enum import Enum

class SessionOutcome(str, Enum):
    BREAKTHROUGH = "Breakthrough"
    PROGRESS = "Progress"
    MAINTENANCE = "Maintenance"
    CHALLENGE = "Challenge"

class ActionItemPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SessionProcessingEngine:
    """
    AI-powered session processing engine for Sarah Cave's executive coaching business.
    Transforms raw session notes into structured summaries and extracts actionable insights.
    """
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.session_prompt = self._get_session_prompt()
        self.action_item_prompt = self._get_action_item_prompt()
    
    def _get_session_prompt(self) -> str:
        """System prompt for session note processing based on Sarah Cave's coaching methodology."""
        return """
You are Sarah Cave's expert session analysis specialist. Your role is to transform raw coaching session notes into structured, professional summaries that capture key leadership insights and client progress.

Your Expertise:
- Executive coaching methodology and leadership development frameworks
- Session outcome assessment and progress tracking
- Client health signal identification (engagement, satisfaction, growth)
- Professional coaching documentation standards

Core Responsibilities:
1. Create clear, concise session summaries (100-200 words)
2. Identify key leadership themes and breakthroughs
3. Assess session outcome: Breakthrough, Progress, Maintenance, or Challenge
4. Extract client health indicators (satisfaction, engagement, momentum)
5. Flag any concerning patterns or red flags

Session Summary Structure:
- **Session Focus**: Primary topics and leadership challenges addressed
- **Key Insights**: Main breakthroughs or learning moments
- **Client Engagement**: Energy level, participation, receptiveness (1-10 scale)
- **Progress Assessment**: Movement toward goals and action items
- **Next Session Preparation**: Areas to explore or follow up on

Assessment Criteria:
- **Breakthrough** (9-10/10): Major insights, high energy, clear action commitment
- **Progress** (7-8/10): Steady advancement, good engagement, practical next steps
- **Maintenance** (5-6/10): Status quo, moderate engagement, incremental progress
- **Challenge** (1-4/10): Low energy, resistance, unclear progress, or obstacles

Client Health Signals:
- High satisfaction: Enthusiasm, gratitude, clear value perception
- Medium satisfaction: Engaged but routine, some value recognition
- Low satisfaction: Disengagement, questioning value, or frustration
- Red flags: Cancellations, payment delays, shortened sessions, lack of implementation

Output Format:
- Session Summary: Professional narrative summary
- Session Outcome: Single classification (Breakthrough/Progress/Maintenance/Challenge)
- Client Satisfaction: Scale 1-10 with brief reasoning
- Health Score: Overall client health assessment (Healthy/At Risk/Critical)
- Red Flags: List any concerning indicators
- Next Session Focus: Recommended areas for follow-up

Constraints:
- Maintain complete confidentiality and professionalism
- Focus on leadership development and business outcomes
- Never include personal details that aren't relevant to coaching goals
- Always provide actionable insights for session progression
"""

    def _get_action_item_prompt(self) -> str:
        """System prompt for action item extraction from session notes."""
        return """
You are an expert action item extraction specialist for executive coaching sessions. Your role is to identify and structure actionable commitments from raw session discussions.

Extraction Expertise:
- Distinguish between coach suggestions and client commitments
- Prioritize action items by impact and urgency
- Set realistic timeframes for executive schedules
- Connect actions to leadership development goals

Action Item Criteria:
- **Must be client commitments** (not coach suggestions)
- **Specific and measurable** outcomes
- **Realistic timeframes** for busy executives
- **Clear success metrics** when possible

Priority Classification:
- **High Priority**: Critical for goal achievement, urgent timeline, high impact
- **Medium Priority**: Important progress, moderate urgency, clear value
- **Low Priority**: Nice-to-have, flexible timeline, incremental improvement

Timeframe Guidelines:
- Urgent actions: 1-3 days
- Weekly commitments: 7 days
- Monthly goals: 30 days
- Quarterly objectives: 90 days

Output Format per Action Item:
- Action Description: Clear, specific task or commitment
- Priority Level: High/Medium/Low
- Due Date: Realistic completion timeframe
- Success Metric: How completion will be measured
- Leadership Development Area: Which skill/competency this supports

Quality Standards:
- Only extract genuine client commitments
- Avoid vague or unmeasurable actions
- Connect each action to leadership growth
- Prioritize based on client's stated goals
- Consider executive time constraints and competing priorities
"""

    async def process_session_intelligence(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw session notes using AI to generate structured summary and extract action items.
        
        Args:
            session_data: Dictionary containing session information:
                - client_name: Client's name
                - session_date: Session date (ISO format)
                - session_duration: Duration in minutes
                - raw_notes: Raw session notes from Sarah
                - session_type: Type of session (1-on-1, group, intensive)
                - leadership_model: Leadership model/framework used
                - client_goals: Current client objectives
                - previous_actions: Previous session action items
        
        Returns:
            Dictionary with processed session results:
                - session_summary: AI-generated structured summary
                - session_outcome: Breakthrough/Progress/Maintenance/Challenge
                - client_satisfaction: 1-10 satisfaction assessment
                - health_score: Overall client health assessment
                - action_items: List of extracted action items
                - red_flags: List of concerning indicators
                - next_session_focus: Recommended follow-up areas
                - processing_metadata: Timestamp and confidence scores
        """
        
        # Prepare session context for AI analysis
        session_context = self._prepare_session_context(session_data)
        
        try:
            # Process session summary
            summary_result = await self._generate_session_summary(session_context)
            
            # Extract action items
            action_items = await self._extract_action_items(session_context, session_data)
            
            # Combine results
            processing_result = {
                **summary_result,
                'action_items': action_items,
                'processing_metadata': {
                    'processed_at': datetime.utcnow().isoformat(),
                    'processing_version': '1.0',
                    'ai_confidence': summary_result.get('ai_confidence', 0.85),
                    'total_action_items': len(action_items)
                }
            }
            
            return processing_result
            
        except Exception as e:
            # Fallback to rule-based processing if AI fails
            return self._fallback_rule_based_processing(session_data, str(e))
    
    def _prepare_session_context(self, session_data: Dict[str, Any]) -> str:
        """Prepare structured session context for AI analysis."""
        context_parts = []
        
        # Session Metadata
        context_parts.append(f"Client: {session_data.get('client_name', 'Unknown')}")
        context_parts.append(f"Session Date: {session_data.get('session_date', 'Not provided')}")
        context_parts.append(f"Duration: {session_data.get('session_duration', 'Not specified')} minutes")
        context_parts.append(f"Session Type: {session_data.get('session_type', 'Standard coaching')}")
        
        # Leadership Context
        if session_data.get('leadership_model'):
            context_parts.append(f"Leadership Framework: {session_data['leadership_model']}")
        
        if session_data.get('client_goals'):
            context_parts.append(f"Current Client Goals: {session_data['client_goals']}")
        
        # Previous Context
        if session_data.get('previous_actions'):
            context_parts.append(f"Previous Action Items: {session_data['previous_actions']}")
        
        # Raw Session Notes
        raw_notes = session_data.get('raw_notes', '')
        context_parts.append(f"\nSession Notes:\n{raw_notes}")
        
        return "\n".join(context_parts)
    
    async def _generate_session_summary(self, session_context: str) -> Dict[str, Any]:
        """Generate structured session summary using AI."""
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.session_prompt},
                    {"role": "user", "content": f"Please analyze this coaching session:\n\n{session_context}"}
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=600
            )
            
            ai_response = response.choices[0].message.content
            summary_result = self._parse_session_response(ai_response)
            
            return summary_result
            
        except Exception as e:
            raise Exception(f"Session summary generation failed: {str(e)}")
    
    async def _extract_action_items(self, session_context: str, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and structure action items from session notes."""
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.action_item_prompt},
                    {"role": "user", "content": f"Extract action items from this session:\n\n{session_context}"}
                ],
                temperature=0.2,  # Very low temperature for precise extraction
                max_tokens=400
            )
            
            ai_response = response.choices[0].message.content
            action_items = self._parse_action_items_response(ai_response, session_data)
            
            return action_items
            
        except Exception as e:
            # Return basic action items if AI extraction fails
            return self._extract_basic_action_items(session_data)
    
    def _parse_session_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured session summary."""
        
        # Extract session summary
        summary_lines = []
        outcome = SessionOutcome.PROGRESS
        satisfaction = 7
        health_score = "Healthy"
        red_flags = []
        next_focus = ""
        
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if 'session summary' in line.lower() or 'summary:' in line.lower():
                current_section = 'summary'
                continue
            elif 'session outcome' in line.lower() or 'outcome:' in line.lower():
                current_section = 'outcome'
                continue
            elif 'client satisfaction' in line.lower() or 'satisfaction:' in line.lower():
                current_section = 'satisfaction'
                continue
            elif 'health score' in line.lower() or 'health:' in line.lower():
                current_section = 'health'
                continue
            elif 'red flags' in line.lower() or 'flags:' in line.lower():
                current_section = 'flags'
                continue
            elif 'next session' in line.lower() or 'next focus' in line.lower():
                current_section = 'next'
                continue
            
            # Parse content based on section
            if current_section == 'summary' and not any(keyword in line.lower() for keyword in ['outcome:', 'satisfaction:', 'health:']):
                summary_lines.append(line)
            elif current_section == 'outcome':
                if 'breakthrough' in line.lower():
                    outcome = SessionOutcome.BREAKTHROUGH
                elif 'challenge' in line.lower():
                    outcome = SessionOutcome.CHALLENGE
                elif 'maintenance' in line.lower():
                    outcome = SessionOutcome.MAINTENANCE
                else:
                    outcome = SessionOutcome.PROGRESS
            elif current_section == 'satisfaction':
                # Extract number from satisfaction line
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    satisfaction = min(10, max(1, numbers[0]))
            elif current_section == 'health':
                if 'at risk' in line.lower():
                    health_score = "At Risk"
                elif 'critical' in line.lower():
                    health_score = "Critical"
                else:
                    health_score = "Healthy"
            elif current_section == 'flags':
                if line.startswith('-') or line.startswith('•'):
                    red_flags.append(line.lstrip('- •'))
            elif current_section == 'next':
                next_focus += line + " "
        
        session_summary = " ".join(summary_lines).strip()
        if not session_summary:
            session_summary = "Session focused on leadership development with client engagement and progress toward established goals."
        
        return {
            'session_summary': session_summary,
            'session_outcome': outcome.value,
            'client_satisfaction': satisfaction,
            'health_score': health_score,
            'red_flags': red_flags,
            'next_session_focus': next_focus.strip(),
            'ai_confidence': 0.85
        }
    
    def _parse_action_items_response(self, ai_response: str, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into structured action items."""
        action_items = []
        current_item = {}
        
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Start of new action item
            if line.startswith('Action:') or line.startswith('1.') or line.startswith('-'):
                if current_item:
                    action_items.append(self._finalize_action_item(current_item, session_data))
                current_item = {'action': line.replace('Action:', '').strip().lstrip('123456789.- ')}
            elif 'priority:' in line.lower():
                priority = line.lower().replace('priority:', '').strip()
                if 'high' in priority:
                    current_item['priority'] = ActionItemPriority.HIGH
                elif 'low' in priority:
                    current_item['priority'] = ActionItemPriority.LOW
                else:
                    current_item['priority'] = ActionItemPriority.MEDIUM
            elif 'due:' in line.lower() or 'timeframe:' in line.lower():
                current_item['due_date'] = self._parse_due_date(line)
            elif 'success:' in line.lower() or 'metric:' in line.lower():
                current_item['success_metric'] = line.split(':', 1)[1].strip()
            elif 'leadership:' in line.lower() or 'development:' in line.lower():
                current_item['leadership_area'] = line.split(':', 1)[1].strip()
        
        # Don't forget the last item
        if current_item:
            action_items.append(self._finalize_action_item(current_item, session_data))
        
        return action_items[:5]  # Limit to 5 action items per session
    
    def _finalize_action_item(self, item: Dict[str, Any], session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize action item with defaults and validation."""
        return {
            'action_description': item.get('action', 'Follow up on session discussion'),
            'priority_level': item.get('priority', ActionItemPriority.MEDIUM).value,
            'due_date': item.get('due_date', self._calculate_default_due_date()),
            'success_metric': item.get('success_metric', 'Completion confirmed in next session'),
            'leadership_development_area': item.get('leadership_area', 'Leadership Growth'),
            'client_name': session_data.get('client_name', ''),
            'session_date': session_data.get('session_date', datetime.utcnow().isoformat()),
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _parse_due_date(self, date_line: str) -> str:
        """Parse due date from AI response."""
        date_line = date_line.lower()
        now = datetime.utcnow()
        
        if 'week' in date_line:
            due_date = now + timedelta(days=7)
        elif 'month' in date_line:
            due_date = now + timedelta(days=30)
        elif 'days' in date_line:
            # Extract number of days
            numbers = [int(s) for s in date_line.split() if s.isdigit()]
            days = numbers[0] if numbers else 7
            due_date = now + timedelta(days=days)
        else:
            due_date = now + timedelta(days=7)  # Default to 1 week
        
        return due_date.isoformat()
    
    def _calculate_default_due_date(self) -> str:
        """Calculate default due date for action items."""
        return (datetime.utcnow() + timedelta(days=14)).isoformat()
    
    def _extract_basic_action_items(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract basic action items when AI processing fails."""
        raw_notes = session_data.get('raw_notes', '').lower()
        basic_items = []
        
        # Look for action-oriented keywords
        action_keywords = ['will', 'commit', 'action', 'follow up', 'implement', 'practice', 'review']
        
        sentences = raw_notes.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence for keyword in action_keywords) and len(sentence) > 20:
                basic_items.append({
                    'action_description': sentence.capitalize(),
                    'priority_level': ActionItemPriority.MEDIUM.value,
                    'due_date': self._calculate_default_due_date(),
                    'success_metric': 'Progress discussed in next session',
                    'leadership_development_area': 'Leadership Development',
                    'client_name': session_data.get('client_name', ''),
                    'session_date': session_data.get('session_date', datetime.utcnow().isoformat()),
                    'created_at': datetime.utcnow().isoformat()
                })
                
                if len(basic_items) >= 3:  # Limit basic extraction
                    break
        
        # Ensure at least one action item
        if not basic_items:
            basic_items.append({
                'action_description': 'Implement insights from today\'s coaching session',
                'priority_level': ActionItemPriority.MEDIUM.value,
                'due_date': self._calculate_default_due_date(),
                'success_metric': 'Progress reviewed in next session',
                'leadership_development_area': 'Leadership Implementation',
                'client_name': session_data.get('client_name', ''),
                'session_date': session_data.get('session_date', datetime.utcnow().isoformat()),
                'created_at': datetime.utcnow().isoformat()
            })
        
        return basic_items
    
    def _fallback_rule_based_processing(self, session_data: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback processing when AI service fails."""
        raw_notes = session_data.get('raw_notes', '')
        
        # Basic sentiment analysis
        positive_words = ['breakthrough', 'progress', 'excellent', 'great', 'successful', 'engaged']
        negative_words = ['challenge', 'difficult', 'struggle', 'frustrated', 'stuck', 'resistance']
        
        positive_count = sum(1 for word in positive_words if word in raw_notes.lower())
        negative_count = sum(1 for word in negative_words if word in raw_notes.lower())
        
        # Determine outcome and satisfaction
        if positive_count > negative_count + 1:
            outcome = SessionOutcome.PROGRESS
            satisfaction = 8
            health_score = "Healthy"
        elif negative_count > positive_count:
            outcome = SessionOutcome.CHALLENGE
            satisfaction = 5
            health_score = "At Risk"
        else:
            outcome = SessionOutcome.MAINTENANCE
            satisfaction = 6
            health_score = "Healthy"
        
        # Generate basic summary
        word_count = len(raw_notes.split())
        session_summary = f"Session covered key leadership topics with {session_data.get('client_name', 'client')}. "
        session_summary += f"Discussion included {word_count} words of content focusing on leadership development and goal progression."
        
        # Extract basic action items
        action_items = self._extract_basic_action_items(session_data)
        
        return {
            'session_summary': session_summary,
            'session_outcome': outcome.value,
            'client_satisfaction': satisfaction,
            'health_score': health_score,
            'red_flags': [f"AI processing failed: {error}"],
            'next_session_focus': "Follow up on session insights and action item progress",
            'action_items': action_items,
            'processing_metadata': {
                'processed_at': datetime.utcnow().isoformat(),
                'processing_version': '1.0-fallback',
                'ai_confidence': 0.6,
                'total_action_items': len(action_items),
                'fallback_used': True,
                'error': error
            }
        }

# Public interface function for webhook integration
async def process_session_intelligence(session_data: Dict[str, Any], openai_api_key: str) -> Dict[str, Any]:
    """
    Main function for processing session notes - called by webhook automation.
    
    Args:
        session_data: Session information from Airtable webhook
        openai_api_key: OpenAI API key for AI processing
    
    Returns:
        Comprehensive session processing results
    """
    engine = SessionProcessingEngine(openai_api_key)
    return await engine.process_session_intelligence(session_data)

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test session data
    test_session = {
        'client_name': 'John Smith',
        'session_date': '2024-12-09',
        'session_duration': 60,
        'session_type': '1-on-1 Executive Coaching',
        'leadership_model': 'SWOT Analysis',
        'client_goals': 'Improve team leadership and conflict resolution',
        'raw_notes': '''
        Great session with John today. He came in with energy and was really engaged throughout.
        We worked on his team conflict situation with the engineering and product teams.
        
        Key breakthrough: John realized he's been avoiding difficult conversations because he wants to be liked.
        This is actually making the conflicts worse. We discussed how authentic leadership requires difficult conversations.
        
        He committed to having a direct conversation with his VP of Product about the roadmap conflicts by Wednesday.
        Also agreed to implement weekly team alignment meetings starting next Monday.
        
        John seemed really motivated and said this was the most valuable session we've had. He's making progress
        on his goal of being more direct while maintaining relationships.
        
        For next session: Focus on how the difficult conversation went and work on delegation strategies.
        '''
    }
    
    async def test_processing():
        # You would pass actual OpenAI API key here
        result = await process_session_intelligence(test_session, 'test-api-key')
        print(json.dumps(result, indent=2))
    
    # asyncio.run(test_processing())  # Uncomment to test