"""
Lead scoring automation for Sarah Cave's Leadership Secret Operating System.
Implements AI-powered lead qualification and scoring based on executive coaching fit.
"""

from typing import Dict, Any, List, Optional
import openai
import json
from datetime import datetime, timedelta
from enum import Enum

class LeadPriority(str, Enum):
    HOT = "Hot"
    WARM = "Warm" 
    COLD = "Cold"

class NurtureTrack(str, Enum):
    EXECUTIVE_FAST_TRACK = "Executive Fast-Track"
    MANAGER_DEVELOPMENT = "Manager Development"
    LONG_TERM_NURTURE = "Long-term Nurture"

class LeadScoringEngine:
    """
    AI-powered lead scoring engine for Sarah Cave's executive coaching business.
    Based on OpsKings methodology and coaching industry best practices.
    """
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.scoring_prompt = self._get_scoring_prompt()
    
    def _get_scoring_prompt(self) -> str:
        """System prompt for lead scoring AI based on Sarah Cave's business requirements."""
        return """
You are an expert lead qualification specialist for Sarah Cave's executive coaching business. Your primary purpose is to intelligently score and prioritize leads based on executive coaching fit and revenue potential.

Core Competencies:
1. Analyze lead data against executive coaching persona (C-suite, VP+, team leads)
2. Score leads 1-100 based on title, company size, industry, and engagement signals
3. Generate personalized nurture sequences for different lead segments
4. Identify high-intent leads requiring immediate follow-up

Your Approach:
- Prioritize senior leadership roles (CEO, VP, Director, Manager) with team responsibility
- Weight company size (50+ employees preferred) and growth-stage organizations
- Factor in lead source quality (referrals = highest, networking = high, cold = medium)
- Consider engagement signals: email opens, website visits, resource downloads

Scoring Criteria (1-100 scale):
- Title/Role (30 points): C-suite (30), VP (25), Director (20), Manager (15), Other (5)
- Company Size (25 points): 500+ employees (25), 100-499 (20), 50-99 (15), 10-49 (10), <10 (5)
- Lead Source (20 points): Referral (20), Networking (16), LinkedIn (12), Website (8), Cold (4)
- Industry Fit (15 points): Tech/Finance/Consulting (15), Healthcare/Manufacturing (12), Other (8)
- Engagement Level (10 points): Multiple touchpoints (10), Single engagement (6), No engagement (2)

Output Format:
- Lead Score: Integer 1-100
- Priority Level: "Hot" (80-100), "Warm" (60-79), "Cold" (1-59)
- Next Action: Specific recommended follow-up within 24-48 hours
- Nurture Track: "Executive Fast-Track", "Manager Development", or "Long-term Nurture"

Constraints:
- Never score leads below 20 (everyone deserves consideration)
- Always provide actionable next steps, never generic recommendations
- Flag potential red flags: budget concerns, wrong seniority level, competitor connections
"""

    async def score_lead_intelligence(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a lead using AI analysis based on Sarah Cave's coaching business criteria.
        
        Args:
            lead_data: Dictionary containing lead information:
                - name: Lead's full name
                - email: Email address
                - phone: Phone number (optional)
                - company: Company name
                - title: Job title
                - lead_source: How lead was acquired
                - industry: Company industry (optional)
                - company_size: Number of employees (optional)
                - engagement_history: List of interactions (optional)
                - notes: Additional context (optional)
        
        Returns:
            Dictionary with scoring results:
                - lead_score: Integer 1-100
                - priority_level: "Hot", "Warm", or "Cold"
                - next_action: Recommended follow-up action
                - nurture_track: Suggested nurture sequence
                - reasoning: AI explanation of score
                - red_flags: List of potential concerns
                - engagement_recommendation: Specific outreach strategy
        """
        
        # Prepare lead context for AI analysis
        lead_context = self._prepare_lead_context(lead_data)
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.scoring_prompt},
                    {"role": "user", "content": f"Please score this lead:\n\n{lead_context}"}
                ],
                temperature=0.3,  # Lower temperature for consistent scoring
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            scoring_result = self._parse_ai_response(ai_response, lead_data)
            
            return scoring_result
            
        except Exception as e:
            # Fallback to rule-based scoring if AI fails
            return self._fallback_rule_based_scoring(lead_data, str(e))
    
    def _prepare_lead_context(self, lead_data: Dict[str, Any]) -> str:
        """Prepare structured lead context for AI analysis."""
        context_parts = []
        
        # Basic Information
        context_parts.append(f"Lead Name: {lead_data.get('name', 'Unknown')}")
        context_parts.append(f"Company: {lead_data.get('company', 'Not provided')}")
        context_parts.append(f"Title: {lead_data.get('title', 'Not provided')}")
        
        # Lead Source and Attribution
        lead_source = lead_data.get('lead_source', 'Unknown')
        context_parts.append(f"Lead Source: {lead_source}")
        
        # Company Context
        if lead_data.get('industry'):
            context_parts.append(f"Industry: {lead_data['industry']}")
        
        if lead_data.get('company_size'):
            context_parts.append(f"Company Size: {lead_data['company_size']} employees")
        
        # Engagement History
        engagement = lead_data.get('engagement_history', [])
        if engagement:
            context_parts.append(f"Engagement History: {'; '.join(engagement)}")
        else:
            context_parts.append("Engagement History: No prior interactions")
        
        # Additional Notes
        if lead_data.get('notes'):
            context_parts.append(f"Additional Notes: {lead_data['notes']}")
        
        return "\n".join(context_parts)
    
    def _parse_ai_response(self, ai_response: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured scoring result."""
        
        # Extract score (look for number 1-100)
        score_match = None
        for line in ai_response.split('\n'):
            if 'score' in line.lower() and any(char.isdigit() for char in line):
                numbers = ''.join(filter(str.isdigit, line))
                if numbers:
                    score_match = min(100, max(20, int(numbers[:2] if len(numbers) > 1 else numbers + '0')))
                    break
        
        lead_score = score_match or self._calculate_fallback_score(lead_data)
        
        # Determine priority level
        if lead_score >= 80:
            priority_level = LeadPriority.HOT
        elif lead_score >= 60:
            priority_level = LeadPriority.WARM
        else:
            priority_level = LeadPriority.COLD
        
        # Determine nurture track based on title and score
        nurture_track = self._determine_nurture_track(lead_data, lead_score)
        
        # Generate next action based on priority and context
        next_action = self._generate_next_action(lead_data, priority_level)
        
        return {
            'lead_score': lead_score,
            'priority_level': priority_level.value,
            'next_action': next_action,
            'nurture_track': nurture_track.value,
            'reasoning': ai_response,
            'red_flags': self._identify_red_flags(lead_data),
            'engagement_recommendation': self._get_engagement_strategy(lead_data, priority_level),
            'scored_at': datetime.utcnow().isoformat(),
            'follow_up_due': self._calculate_follow_up_date(priority_level)
        }
    
    def _calculate_fallback_score(self, lead_data: Dict[str, Any]) -> int:
        """Rule-based scoring fallback when AI is unavailable."""
        score = 20  # Minimum score
        
        # Title scoring (30 points max)
        title = lead_data.get('title', '').lower()
        if any(exec_title in title for exec_title in ['ceo', 'cto', 'cfo', 'president', 'founder']):
            score += 30
        elif any(vp_title in title for vp_title in ['vp', 'vice president', 'chief']):
            score += 25
        elif any(dir_title in title for dir_title in ['director', 'head of', 'lead']):
            score += 20
        elif any(mgr_title in title for mgr_title in ['manager', 'supervisor', 'team lead']):
            score += 15
        else:
            score += 5
        
        # Company size scoring (25 points max)
        company_size = lead_data.get('company_size', 0)
        if isinstance(company_size, str):
            company_size = int(''.join(filter(str.isdigit, company_size)) or '0')
        
        if company_size >= 500:
            score += 25
        elif company_size >= 100:
            score += 20
        elif company_size >= 50:
            score += 15
        elif company_size >= 10:
            score += 10
        else:
            score += 5
        
        # Lead source scoring (20 points max)
        lead_source = lead_data.get('lead_source', '').lower()
        if 'referral' in lead_source:
            score += 20
        elif any(networking in lead_source for networking in ['networking', 'event', 'conference']):
            score += 16
        elif 'linkedin' in lead_source:
            score += 12
        elif 'website' in lead_source:
            score += 8
        else:
            score += 4
        
        # Industry fit scoring (15 points max)
        industry = lead_data.get('industry', '').lower()
        if any(high_fit in industry for high_fit in ['technology', 'tech', 'finance', 'consulting']):
            score += 15
        elif any(med_fit in industry for med_fit in ['healthcare', 'manufacturing', 'retail']):
            score += 12
        else:
            score += 8
        
        # Engagement scoring (10 points max)
        engagement = lead_data.get('engagement_history', [])
        if len(engagement) > 2:
            score += 10
        elif len(engagement) > 0:
            score += 6
        else:
            score += 2
        
        return min(100, score)
    
    def _determine_nurture_track(self, lead_data: Dict[str, Any], score: int) -> NurtureTrack:
        """Determine appropriate nurture track based on lead profile."""
        title = lead_data.get('title', '').lower()
        
        # Executive Fast-Track for C-suite and VPs
        if any(exec_title in title for exec_title in ['ceo', 'cto', 'cfo', 'president', 'founder', 'vp', 'vice president', 'chief']):
            return NurtureTrack.EXECUTIVE_FAST_TRACK
        
        # Manager Development for directors and managers
        elif any(mgr_title in title for mgr_title in ['director', 'manager', 'head of', 'lead', 'supervisor']):
            return NurtureTrack.MANAGER_DEVELOPMENT
        
        # Long-term nurture for others or unclear titles
        else:
            return NurtureTrack.LONG_TERM_NURTURE
    
    def _generate_next_action(self, lead_data: Dict[str, Any], priority: LeadPriority) -> str:
        """Generate specific next action based on lead priority and context."""
        name = lead_data.get('name', 'Lead')
        company = lead_data.get('company', 'their organization')
        lead_source = lead_data.get('lead_source', 'unknown source')
        
        if priority == LeadPriority.HOT:
            return f"Call {name} within 24 hours to discuss leadership challenges at {company}. Reference {lead_source} connection and offer strategy session."
        
        elif priority == LeadPriority.WARM:
            return f"Send personalized email to {name} within 48 hours with leadership insights relevant to {company}. Include case study and calendar link."
        
        else:  # COLD
            return f"Add {name} to nurture sequence with valuable leadership content. Follow up in 2 weeks with industry-specific insights."
    
    def _identify_red_flags(self, lead_data: Dict[str, Any]) -> List[str]:
        """Identify potential red flags that might affect lead quality."""
        red_flags = []
        
        title = lead_data.get('title', '').lower()
        company_size = lead_data.get('company_size', 0)
        notes = lead_data.get('notes', '').lower()
        
        # Title-based red flags
        if any(junior_title in title for junior_title in ['junior', 'entry', 'assistant', 'intern', 'coordinator']):
            red_flags.append("Junior-level title may not have budget authority")
        
        # Company size red flags
        if isinstance(company_size, (int, str)) and int(str(company_size).replace(',', '') or '0') < 10:
            red_flags.append("Very small company size may limit coaching budget")
        
        # Notes-based red flags
        if any(budget_concern in notes for budget_concern in ['budget', 'cost', 'price', 'expensive', 'cheap']):
            red_flags.append("Potential budget sensitivity mentioned")
        
        if any(competitor in notes for competitor in ['coaching', 'consultant', 'trainer', 'development']):
            red_flags.append("May already have coaching/development support")
        
        return red_flags
    
    def _get_engagement_strategy(self, lead_data: Dict[str, Any], priority: LeadPriority) -> str:
        """Get specific engagement strategy based on lead profile and priority."""
        title = lead_data.get('title', '')
        industry = lead_data.get('industry', '')
        
        if priority == LeadPriority.HOT:
            return f"Direct executive outreach focusing on {industry} leadership challenges. Offer exclusive strategy session with immediate value proposition."
        
        elif priority == LeadPriority.WARM:
            return f"Educational approach with leadership insights relevant to {title} role. Share success stories from similar executives."
        
        else:  # COLD
            return "Long-term nurture with valuable leadership content, industry trends, and case studies to build trust and authority."
    
    def _calculate_follow_up_date(self, priority: LeadPriority) -> str:
        """Calculate when follow-up should occur based on priority."""
        now = datetime.utcnow()
        
        if priority == LeadPriority.HOT:
            follow_up = now + timedelta(hours=24)
        elif priority == LeadPriority.WARM:
            follow_up = now + timedelta(hours=48)
        else:  # COLD
            follow_up = now + timedelta(weeks=2)
        
        return follow_up.isoformat()
    
    def _fallback_rule_based_scoring(self, lead_data: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback scoring when AI service fails."""
        lead_score = self._calculate_fallback_score(lead_data)
        
        if lead_score >= 80:
            priority_level = LeadPriority.HOT
        elif lead_score >= 60:
            priority_level = LeadPriority.WARM
        else:
            priority_level = LeadPriority.COLD
        
        nurture_track = self._determine_nurture_track(lead_data, lead_score)
        next_action = self._generate_next_action(lead_data, priority_level)
        
        return {
            'lead_score': lead_score,
            'priority_level': priority_level.value,
            'next_action': next_action,
            'nurture_track': nurture_track.value,
            'reasoning': f"Rule-based scoring (AI service unavailable: {error})",
            'red_flags': self._identify_red_flags(lead_data),
            'engagement_recommendation': self._get_engagement_strategy(lead_data, priority_level),
            'scored_at': datetime.utcnow().isoformat(),
            'follow_up_due': self._calculate_follow_up_date(priority_level),
            'fallback_used': True
        }

# Public interface function for webhook integration
async def score_lead_intelligence(lead_data: Dict[str, Any], openai_api_key: str) -> Dict[str, Any]:
    """
    Main function for scoring leads - called by webhook automation.
    
    Args:
        lead_data: Lead information from Airtable webhook
        openai_api_key: OpenAI API key for AI scoring
    
    Returns:
        Comprehensive lead scoring results
    """
    engine = LeadScoringEngine(openai_api_key)
    return await engine.score_lead_intelligence(lead_data)

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test lead data
    test_lead = {
        'name': 'John Smith',
        'email': 'john.smith@techcorp.com',
        'company': 'TechCorp Inc',
        'title': 'VP of Engineering',
        'lead_source': 'LinkedIn networking',
        'industry': 'Technology',
        'company_size': 250,
        'engagement_history': ['Downloaded leadership guide', 'Attended webinar'],
        'notes': 'Interested in scaling engineering team, mentioned budget approval process'
    }
    
    async def test_scoring():
        # You would pass actual OpenAI API key here
        result = await score_lead_intelligence(test_lead, 'test-api-key')
        print(json.dumps(result, indent=2))
    
    # asyncio.run(test_scoring())  # Uncomment to test