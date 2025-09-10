"""
Client health monitoring automation for Sarah Cave's Leadership Secret Operating System.
Implements intelligent client health scoring, risk assessment, and proactive alert system.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime, timedelta
from enum import Enum
import openai

class HealthStatus(str, Enum):
    HEALTHY = "Healthy"
    AT_RISK = "At Risk"
    CRITICAL = "Critical"

class RiskCategory(str, Enum):
    ENGAGEMENT = "Engagement Risk"
    FINANCIAL = "Financial Risk"
    SATISFACTION = "Satisfaction Risk"
    PROGRESS = "Progress Risk"

class AlertPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ClientHealthMonitor:
    """
    AI-powered client health monitoring system for Sarah Cave's executive coaching business.
    Analyzes multiple signals to assess client health and identify at-risk clients proactively.
    """
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.health_assessment_prompt = self._get_health_assessment_prompt()
        
        # Health scoring weights
        self.scoring_weights = {
            'session_frequency': 0.25,    # 25% - How often sessions occur
            'payment_behavior': 0.20,     # 20% - Payment timeliness
            'session_satisfaction': 0.20, # 20% - Session satisfaction scores
            'action_item_completion': 0.15, # 15% - Follow-through on commitments  
            'engagement_signals': 0.15,   # 15% - Participation and energy
            'progress_momentum': 0.05     # 5% - Overall goal progress
        }
    
    def _get_health_assessment_prompt(self) -> str:
        """System prompt for AI-powered client health assessment."""
        return """
You are Sarah Cave's expert client health assessment specialist. Your role is to analyze comprehensive client data and identify potential risks before they become problems.

Your Expertise:
- Executive coaching client lifecycle management
- Early warning signal identification for client relationships
- Risk factor analysis and prioritization
- Proactive intervention strategy development
- Client retention and satisfaction optimization

Assessment Framework:
You analyze multiple dimensions of client health to provide comprehensive risk assessment:

1. **Engagement Patterns**
   - Session attendance and punctuality
   - Active participation vs. passive presence
   - Initiative in scheduling and communication
   - Responsiveness to coaching suggestions

2. **Financial Health Signals**
   - Payment timeliness and consistency
   - Invoice inquiry patterns or disputes
   - Budget or cost concerns expressed
   - Value perception indicators

3. **Progress & Satisfaction**
   - Goal achievement momentum
   - Session satisfaction ratings
   - Action item completion rates
   - Enthusiasm and energy levels

4. **Communication Quality**
   - Frequency and tone of communications
   - Proactive vs. reactive engagement
   - Openness to feedback and suggestions
   - Long-term commitment signals

Risk Classification:
- **Healthy (80-100)**: Strong engagement, timely payments, high satisfaction, clear progress
- **At Risk (50-79)**: Some warning signals, declining patterns, moderate concerns
- **Critical (0-49)**: Multiple red flags, immediate intervention needed

Output Requirements:
- Overall Health Score: 0-100 numerical assessment
- Health Status: Healthy/At Risk/Critical classification
- Primary Risk Factors: Top 3 concerns with specific evidence
- Risk Category: Primary category of concern (Engagement/Financial/Satisfaction/Progress)
- Alert Priority: High/Medium/Low urgency for intervention
- Recommended Actions: Specific steps Sarah should take
- Timeline: When intervention should occur

Quality Standards:
- Base assessments on concrete data patterns, not single incidents
- Identify trends over time rather than isolated events
- Provide actionable recommendations with clear next steps
- Consider client's industry, role, and coaching goals context
- Flag urgent situations requiring immediate attention
"""

    async def assess_client_health(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive client health assessment using both AI analysis and rule-based scoring.
        
        Args:
            client_data: Dictionary containing client health information:
                - client_name: Client's name
                - client_id: Unique client identifier
                - session_history: List of recent sessions with dates and satisfaction
                - payment_history: Payment timeliness and amounts
                - action_items: Recent action items and completion status
                - communication_log: Recent communications and responsiveness
                - satisfaction_scores: Historical satisfaction ratings
                - goal_progress: Progress toward stated objectives
                - last_session_date: Most recent session date
                - next_session_date: Scheduled next session
        
        Returns:
            Dictionary with health assessment results:
                - health_score: 0-100 overall health assessment
                - health_status: Healthy/At Risk/Critical
                - risk_factors: List of identified risk factors
                - risk_category: Primary category of concern
                - alert_priority: High/Medium/Low intervention urgency
                - recommended_actions: Specific next steps for Sarah
                - intervention_timeline: When to take action
                - assessment_confidence: AI confidence in assessment
                - monitoring_frequency: How often to reassess
        """
        
        # Calculate base health score using rule-based algorithm
        base_health_score = self._calculate_base_health_score(client_data)
        
        # Prepare client context for AI analysis
        client_context = self._prepare_client_context(client_data, base_health_score)
        
        try:
            # Get AI-powered health assessment
            ai_assessment = await self._get_ai_health_assessment(client_context)
            
            # Combine rule-based scoring with AI insights
            final_assessment = self._combine_assessments(base_health_score, ai_assessment, client_data)
            
            return final_assessment
            
        except Exception as e:
            # Fallback to rule-based assessment if AI fails
            return self._fallback_health_assessment(client_data, base_health_score, str(e))
    
    def _calculate_base_health_score(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate rule-based health score from client data."""
        
        scores = {}
        
        # Session Frequency Score (0-100)
        scores['session_frequency'] = self._score_session_frequency(client_data)
        
        # Payment Behavior Score (0-100)  
        scores['payment_behavior'] = self._score_payment_behavior(client_data)
        
        # Session Satisfaction Score (0-100)
        scores['session_satisfaction'] = self._score_session_satisfaction(client_data)
        
        # Action Item Completion Score (0-100)
        scores['action_item_completion'] = self._score_action_completion(client_data)
        
        # Engagement Signals Score (0-100)
        scores['engagement_signals'] = self._score_engagement_signals(client_data)
        
        # Progress Momentum Score (0-100)
        scores['progress_momentum'] = self._score_progress_momentum(client_data)
        
        # Calculate weighted total score
        total_score = sum(
            scores[category] * self.scoring_weights[category] 
            for category in scores
        )
        
        return {
            'total_score': round(total_score, 1),
            'component_scores': scores,
            'scoring_breakdown': self._generate_scoring_breakdown(scores)
        }
    
    def _score_session_frequency(self, client_data: Dict[str, Any]) -> int:
        """Score based on session frequency and consistency."""
        session_history = client_data.get('session_history', [])
        last_session_date = client_data.get('last_session_date')
        
        if not session_history or not last_session_date:
            return 40  # No data = moderate risk
        
        # Calculate days since last session
        try:
            last_session = datetime.fromisoformat(last_session_date.replace('Z', '+00:00'))
            days_since_last = (datetime.utcnow() - last_session).days
        except:
            return 50  # Invalid date = moderate score
        
        # Score based on recency
        if days_since_last <= 7:
            recency_score = 100
        elif days_since_last <= 14:
            recency_score = 85
        elif days_since_last <= 30:
            recency_score = 70
        elif days_since_last <= 60:
            recency_score = 50
        else:
            recency_score = 20
        
        # Score based on consistency (sessions per month)
        recent_sessions = len([s for s in session_history if s.get('date')])
        if recent_sessions >= 4:
            consistency_score = 100
        elif recent_sessions >= 3:
            consistency_score = 80
        elif recent_sessions >= 2:
            consistency_score = 60
        elif recent_sessions >= 1:
            consistency_score = 40
        else:
            consistency_score = 20
        
        return round((recency_score + consistency_score) / 2)
    
    def _score_payment_behavior(self, client_data: Dict[str, Any]) -> int:
        """Score based on payment timeliness and behavior."""
        payment_history = client_data.get('payment_history', [])
        
        if not payment_history:
            return 80  # No payment issues = good score
        
        total_payments = len(payment_history)
        on_time_payments = sum(1 for p in payment_history if p.get('status') == 'paid_on_time')
        late_payments = sum(1 for p in payment_history if 'late' in str(p.get('status', '')).lower())
        overdue_payments = sum(1 for p in payment_history if 'overdue' in str(p.get('status', '')).lower())
        
        # Calculate payment reliability percentage
        if total_payments == 0:
            return 80
        
        on_time_rate = on_time_payments / total_payments
        late_rate = late_payments / total_payments
        overdue_rate = overdue_payments / total_payments
        
        # Score based on payment patterns
        base_score = int(on_time_rate * 100)
        late_penalty = int(late_rate * 30)  # -30 points max for late payments
        overdue_penalty = int(overdue_rate * 50)  # -50 points max for overdue
        
        final_score = max(0, base_score - late_penalty - overdue_penalty)
        
        # Bonus for perfect payment history
        if on_time_rate == 1.0 and total_payments >= 3:
            final_score = min(100, final_score + 10)
        
        return final_score
    
    def _score_session_satisfaction(self, client_data: Dict[str, Any]) -> int:
        """Score based on session satisfaction ratings."""
        satisfaction_scores = client_data.get('satisfaction_scores', [])
        session_history = client_data.get('session_history', [])
        
        # Extract satisfaction from session history if not in separate field
        if not satisfaction_scores and session_history:
            satisfaction_scores = [
                s.get('satisfaction_score', 7) 
                for s in session_history 
                if s.get('satisfaction_score')
            ]
        
        if not satisfaction_scores:
            return 75  # Default to moderate score if no data
        
        # Convert string scores to numbers
        numeric_scores = []
        for score in satisfaction_scores:
            try:
                if isinstance(score, str):
                    numeric_scores.append(float(score))
                else:
                    numeric_scores.append(float(score))
            except:
                continue
        
        if not numeric_scores:
            return 75
        
        # Calculate average satisfaction
        avg_satisfaction = sum(numeric_scores) / len(numeric_scores)
        
        # Convert 1-10 scale to 0-100 scale
        satisfaction_score = int((avg_satisfaction / 10.0) * 100)
        
        # Factor in trend (recent vs. older scores)
        if len(numeric_scores) >= 3:
            recent_avg = sum(numeric_scores[-3:]) / 3
            older_avg = sum(numeric_scores[:-3]) / max(1, len(numeric_scores[:-3]))
            
            if recent_avg > older_avg:
                satisfaction_score += 5  # Improving trend bonus
            elif recent_avg < older_avg - 0.5:
                satisfaction_score -= 10  # Declining trend penalty
        
        return max(0, min(100, satisfaction_score))
    
    def _score_action_completion(self, client_data: Dict[str, Any]) -> int:
        """Score based on action item completion rates."""
        action_items = client_data.get('action_items', [])
        
        if not action_items:
            return 70  # Default score if no action items
        
        total_items = len(action_items)
        completed_items = sum(1 for item in action_items if item.get('status') == 'completed')
        in_progress_items = sum(1 for item in action_items if item.get('status') == 'in_progress')
        overdue_items = sum(1 for item in action_items if self._is_overdue(item))
        
        # Calculate completion rate
        completion_rate = completed_items / total_items if total_items > 0 else 0
        in_progress_rate = in_progress_items / total_items if total_items > 0 else 0
        overdue_rate = overdue_items / total_items if total_items > 0 else 0
        
        # Base score from completion rate
        base_score = int(completion_rate * 100)
        
        # Partial credit for in-progress items
        progress_bonus = int(in_progress_rate * 30)
        
        # Penalty for overdue items
        overdue_penalty = int(overdue_rate * 40)
        
        final_score = max(0, base_score + progress_bonus - overdue_penalty)
        
        return min(100, final_score)
    
    def _score_engagement_signals(self, client_data: Dict[str, Any]) -> int:
        """Score based on engagement and communication signals."""
        communication_log = client_data.get('communication_log', [])
        session_history = client_data.get('session_history', [])
        
        score = 70  # Start with baseline
        
        # Communication responsiveness
        if communication_log:
            response_times = []
            for comm in communication_log:
                if comm.get('response_time_hours'):
                    response_times.append(comm['response_time_hours'])
            
            if response_times:
                avg_response = sum(response_times) / len(response_times)
                if avg_response <= 24:
                    score += 15  # Quick responder bonus
                elif avg_response <= 48:
                    score += 5   # Reasonable responder
                elif avg_response > 72:
                    score -= 10  # Slow responder penalty
        
        # Session attendance patterns
        if session_history:
            attended_sessions = sum(1 for s in session_history if s.get('attended', True))
            total_scheduled = len(session_history)
            
            if total_scheduled > 0:
                attendance_rate = attended_sessions / total_scheduled
                score += int((attendance_rate - 0.9) * 50)  # Bonus/penalty for attendance
        
        # Proactive engagement signals
        proactive_communications = sum(
            1 for comm in communication_log 
            if comm.get('initiated_by') == 'client'
        )
        if proactive_communications > 2:
            score += 10
        elif proactive_communications == 0 and len(communication_log) > 3:
            score -= 15
        
        return max(0, min(100, score))
    
    def _score_progress_momentum(self, client_data: Dict[str, Any]) -> int:
        """Score based on overall progress toward goals."""
        goal_progress = client_data.get('goal_progress', {})
        session_history = client_data.get('session_history', [])
        
        if not goal_progress and not session_history:
            return 60  # Default moderate score
        
        # Progress percentage from goal tracking
        if isinstance(goal_progress, dict) and 'percentage' in goal_progress:
            progress_pct = goal_progress['percentage']
            base_score = int(progress_pct)
        else:
            # Estimate from session outcomes
            breakthrough_sessions = sum(
                1 for s in session_history 
                if s.get('outcome') == 'Breakthrough'
            )
            progress_sessions = sum(
                1 for s in session_history 
                if s.get('outcome') == 'Progress'
            )
            challenge_sessions = sum(
                1 for s in session_history 
                if s.get('outcome') == 'Challenge'
            )
            
            total_sessions = len(session_history)
            if total_sessions > 0:
                positive_rate = (breakthrough_sessions * 2 + progress_sessions) / total_sessions
                challenge_rate = challenge_sessions / total_sessions
                base_score = int(positive_rate * 50 - challenge_rate * 20 + 50)
            else:
                base_score = 60
        
        return max(0, min(100, base_score))
    
    def _is_overdue(self, action_item: Dict[str, Any]) -> bool:
        """Check if an action item is overdue."""
        due_date_str = action_item.get('due_date')
        if not due_date_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            return datetime.utcnow() > due_date and action_item.get('status') != 'completed'
        except:
            return False
    
    def _generate_scoring_breakdown(self, scores: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate human-readable scoring breakdown."""
        breakdown = []
        
        categories = {
            'session_frequency': 'Session Frequency & Consistency',
            'payment_behavior': 'Payment Timeliness & Reliability', 
            'session_satisfaction': 'Session Satisfaction Ratings',
            'action_item_completion': 'Action Item Follow-through',
            'engagement_signals': 'Communication & Engagement',
            'progress_momentum': 'Goal Progress & Momentum'
        }
        
        for category, score in scores.items():
            category_name = categories.get(category, category)
            weight_pct = int(self.scoring_weights.get(category, 0) * 100)
            
            breakdown.append({
                'category': category_name,
                'score': score,
                'weight_percentage': weight_pct,
                'contribution': round(score * self.scoring_weights.get(category, 0), 1)
            })
        
        return sorted(breakdown, key=lambda x: x['contribution'], reverse=True)
    
    def _prepare_client_context(self, client_data: Dict[str, Any], base_score: Dict[str, Any]) -> str:
        """Prepare structured client context for AI analysis."""
        context_parts = []
        
        # Client Information
        context_parts.append(f"Client: {client_data.get('client_name', 'Unknown')}")
        context_parts.append(f"Client ID: {client_data.get('client_id', 'N/A')}")
        
        # Base Health Score
        context_parts.append(f"\nRule-Based Health Score: {base_score['total_score']}/100")
        context_parts.append("Component Breakdown:")
        for component in base_score['scoring_breakdown']:
            context_parts.append(f"- {component['category']}: {component['score']}/100 (weight: {component['weight_percentage']}%)")
        
        # Session History Summary
        session_history = client_data.get('session_history', [])
        context_parts.append(f"\nRecent Sessions: {len(session_history)} sessions tracked")
        
        if session_history:
            recent_satisfaction = [s.get('satisfaction_score') for s in session_history[-3:] if s.get('satisfaction_score')]
            if recent_satisfaction:
                avg_satisfaction = sum(float(s) for s in recent_satisfaction) / len(recent_satisfaction)
                context_parts.append(f"Recent Average Satisfaction: {avg_satisfaction:.1f}/10")
        
        # Payment Behavior
        payment_history = client_data.get('payment_history', [])
        if payment_history:
            context_parts.append(f"Payment History: {len(payment_history)} payments tracked")
            late_payments = sum(1 for p in payment_history if 'late' in str(p.get('status', '')).lower())
            if late_payments > 0:
                context_parts.append(f"Late Payments: {late_payments}")
        
        # Action Items Status
        action_items = client_data.get('action_items', [])
        if action_items:
            completed = sum(1 for a in action_items if a.get('status') == 'completed')
            context_parts.append(f"Action Items: {completed}/{len(action_items)} completed")
        
        # Communication Patterns
        communication_log = client_data.get('communication_log', [])
        if communication_log:
            context_parts.append(f"Communications: {len(communication_log)} interactions logged")
        
        # Recent Concerns or Notes
        if client_data.get('notes'):
            context_parts.append(f"Notes: {client_data['notes']}")
        
        return "\n".join(context_parts)
    
    async def _get_ai_health_assessment(self, client_context: str) -> Dict[str, Any]:
        """Get AI-powered health assessment and recommendations."""
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.health_assessment_prompt},
                    {"role": "user", "content": f"Assess this client's health:\n\n{client_context}"}
                ],
                temperature=0.2,  # Low temperature for consistent assessments
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_health_response(ai_response)
            
        except Exception as e:
            raise Exception(f"AI health assessment failed: {str(e)}")
    
    def _parse_ai_health_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI health assessment response."""
        
        # Default values
        ai_health_score = 75
        risk_factors = []
        recommendations = []
        
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract health score
            if 'health score' in line.lower() or 'score:' in line.lower():
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    ai_health_score = min(100, max(0, numbers[0]))
            
            # Extract risk factors
            elif 'risk factors' in line.lower() or 'risks:' in line.lower():
                current_section = 'risks'
            elif 'recommended actions' in line.lower() or 'recommendations' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•'):
                if current_section == 'risks':
                    risk_factors.append(line.lstrip('- •'))
                elif current_section == 'recommendations':
                    recommendations.append(line.lstrip('- •'))
        
        # Determine status and priority from score
        if ai_health_score >= 80:
            status = HealthStatus.HEALTHY
            priority = AlertPriority.LOW
        elif ai_health_score >= 50:
            status = HealthStatus.AT_RISK
            priority = AlertPriority.MEDIUM
        else:
            status = HealthStatus.CRITICAL
            priority = AlertPriority.HIGH
        
        return {
            'ai_health_score': ai_health_score,
            'ai_status': status,
            'ai_priority': priority,
            'ai_risk_factors': risk_factors,
            'ai_recommendations': recommendations,
            'ai_confidence': 0.85
        }
    
    def _combine_assessments(self, base_score: Dict[str, Any], ai_assessment: Dict[str, Any], client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine rule-based and AI assessments into final health report."""
        
        # Weighted combination of scores
        rule_based_score = base_score['total_score']
        ai_score = ai_assessment['ai_health_score']
        
        # 70% rule-based, 30% AI adjustment
        final_score = round(rule_based_score * 0.7 + ai_score * 0.3, 1)
        
        # Determine final health status
        if final_score >= 80:
            health_status = HealthStatus.HEALTHY
        elif final_score >= 50:
            health_status = HealthStatus.AT_RISK
        else:
            health_status = HealthStatus.CRITICAL
        
        # Determine alert priority
        if health_status == HealthStatus.CRITICAL:
            alert_priority = AlertPriority.HIGH
        elif health_status == HealthStatus.AT_RISK:
            alert_priority = AlertPriority.MEDIUM
        else:
            alert_priority = AlertPriority.LOW
        
        # Identify primary risk category
        risk_category = self._identify_primary_risk_category(base_score['component_scores'])
        
        # Generate final recommendations
        recommendations = self._generate_recommendations(health_status, risk_category, ai_assessment['ai_recommendations'])
        
        return {
            'client_name': client_data.get('client_name', 'Unknown'),
            'client_id': client_data.get('client_id', 'N/A'),
            'health_score': final_score,
            'health_status': health_status.value,
            'alert_priority': alert_priority.value,
            'risk_category': risk_category.value,
            'risk_factors': ai_assessment['ai_risk_factors'],
            'recommended_actions': recommendations,
            'intervention_timeline': self._calculate_intervention_timeline(health_status, alert_priority),
            'monitoring_frequency': self._calculate_monitoring_frequency(health_status),
            'component_breakdown': base_score['scoring_breakdown'],
            'assessment_confidence': ai_assessment['ai_confidence'],
            'assessed_at': datetime.utcnow().isoformat(),
            'next_assessment_due': self._calculate_next_assessment_date(health_status)
        }
    
    def _identify_primary_risk_category(self, component_scores: Dict[str, int]) -> RiskCategory:
        """Identify the primary category of risk based on component scores."""
        
        # Find lowest scoring components
        sorted_scores = sorted(component_scores.items(), key=lambda x: x[1])
        lowest_category = sorted_scores[0][0]
        
        # Map to risk categories
        category_mapping = {
            'session_frequency': RiskCategory.ENGAGEMENT,
            'payment_behavior': RiskCategory.FINANCIAL,
            'session_satisfaction': RiskCategory.SATISFACTION,
            'action_item_completion': RiskCategory.PROGRESS,
            'engagement_signals': RiskCategory.ENGAGEMENT,
            'progress_momentum': RiskCategory.PROGRESS
        }
        
        return category_mapping.get(lowest_category, RiskCategory.ENGAGEMENT)
    
    def _generate_recommendations(self, health_status: HealthStatus, risk_category: RiskCategory, ai_recommendations: List[str]) -> List[str]:
        """Generate specific recommendations based on health status and risk category."""
        
        recommendations = ai_recommendations[:3]  # Start with AI recommendations
        
        # Add category-specific recommendations
        if risk_category == RiskCategory.FINANCIAL:
            recommendations.extend([
                "Review payment terms and address any billing concerns",
                "Consider payment plan options if cash flow is an issue",
                "Reassess value proposition and ROI demonstration"
            ])
        elif risk_category == RiskCategory.ENGAGEMENT:
            recommendations.extend([
                "Schedule check-in call to assess engagement levels",
                "Explore session format changes to increase participation", 
                "Review coaching goals alignment with current priorities"
            ])
        elif risk_category == RiskCategory.SATISFACTION:
            recommendations.extend([
                "Conduct satisfaction survey to identify specific concerns",
                "Adjust coaching approach based on client preferences",
                "Schedule additional session time to address satisfaction issues"
            ])
        elif risk_category == RiskCategory.PROGRESS:
            recommendations.extend([
                "Review goal setting and create more achievable milestones",
                "Increase action item support and follow-up frequency",
                "Consider intensive session format for breakthrough progress"
            ])
        
        # Health status specific recommendations
        if health_status == HealthStatus.CRITICAL:
            recommendations.insert(0, "URGENT: Schedule immediate client retention conversation")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_intervention_timeline(self, health_status: HealthStatus, alert_priority: AlertPriority) -> str:
        """Calculate when intervention should occur."""
        
        if health_status == HealthStatus.CRITICAL:
            return "Within 24 hours"
        elif health_status == HealthStatus.AT_RISK:
            return "Within 1 week"
        else:
            return "Next scheduled session"
    
    def _calculate_monitoring_frequency(self, health_status: HealthStatus) -> str:
        """Calculate how often to reassess client health."""
        
        if health_status == HealthStatus.CRITICAL:
            return "Daily until improvement"
        elif health_status == HealthStatus.AT_RISK:
            return "Weekly assessment"
        else:
            return "Monthly assessment"
    
    def _calculate_next_assessment_date(self, health_status: HealthStatus) -> str:
        """Calculate when next assessment should occur."""
        
        now = datetime.utcnow()
        
        if health_status == HealthStatus.CRITICAL:
            next_assessment = now + timedelta(days=1)
        elif health_status == HealthStatus.AT_RISK:
            next_assessment = now + timedelta(days=7)
        else:
            next_assessment = now + timedelta(days=30)
        
        return next_assessment.isoformat()
    
    def _fallback_health_assessment(self, client_data: Dict[str, Any], base_score: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback assessment when AI service fails."""
        
        rule_based_score = base_score['total_score']
        
        # Determine health status from rule-based score
        if rule_based_score >= 80:
            health_status = HealthStatus.HEALTHY
            alert_priority = AlertPriority.LOW
        elif rule_based_score >= 50:
            health_status = HealthStatus.AT_RISK
            alert_priority = AlertPriority.MEDIUM
        else:
            health_status = HealthStatus.CRITICAL
            alert_priority = AlertPriority.HIGH
        
        risk_category = self._identify_primary_risk_category(base_score['component_scores'])
        
        # Generate basic recommendations
        basic_recommendations = [
            "Monitor client engagement closely",
            "Ensure regular session scheduling",
            "Follow up on outstanding action items"
        ]
        
        return {
            'client_name': client_data.get('client_name', 'Unknown'),
            'client_id': client_data.get('client_id', 'N/A'),
            'health_score': rule_based_score,
            'health_status': health_status.value,
            'alert_priority': alert_priority.value,
            'risk_category': risk_category.value,
            'risk_factors': [f"AI assessment failed: {error}"],
            'recommended_actions': basic_recommendations,
            'intervention_timeline': self._calculate_intervention_timeline(health_status, alert_priority),
            'monitoring_frequency': self._calculate_monitoring_frequency(health_status),
            'component_breakdown': base_score['scoring_breakdown'],
            'assessment_confidence': 0.7,
            'assessed_at': datetime.utcnow().isoformat(),
            'next_assessment_due': self._calculate_next_assessment_date(health_status),
            'fallback_used': True,
            'error': error
        }

# Public interface function for webhook integration
async def assess_client_health_intelligence(client_data: Dict[str, Any], openai_api_key: str) -> Dict[str, Any]:
    """
    Main function for client health assessment - called by webhook automation.
    
    Args:
        client_data: Client health information from Airtable webhook
        openai_api_key: OpenAI API key for AI assessment
    
    Returns:
        Comprehensive client health assessment results
    """
    monitor = ClientHealthMonitor(openai_api_key)
    return await monitor.assess_client_health(client_data)

# Batch processing for daily health assessments
async def batch_assess_client_health(client_list: List[Dict[str, Any]], openai_api_key: str) -> List[Dict[str, Any]]:
    """
    Batch process client health assessments for daily monitoring.
    
    Args:
        client_list: List of client data dictionaries
        openai_api_key: OpenAI API key for AI assessments
    
    Returns:
        List of health assessment results
    """
    monitor = ClientHealthMonitor(openai_api_key)
    
    assessments = []
    for client_data in client_list:
        try:
            assessment = await monitor.assess_client_health(client_data)
            assessments.append(assessment)
        except Exception as e:
            # Continue with other clients if one fails
            fallback = monitor._fallback_health_assessment(client_data, {'total_score': 70}, str(e))
            assessments.append(fallback)
    
    return assessments

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test client data
    test_client = {
        'client_name': 'John Smith',
        'client_id': 'client-123',
        'last_session_date': '2024-12-05',
        'session_history': [
            {'date': '2024-12-05', 'satisfaction_score': 8, 'attended': True, 'outcome': 'Progress'},
            {'date': '2024-11-28', 'satisfaction_score': 9, 'attended': True, 'outcome': 'Breakthrough'},
            {'date': '2024-11-21', 'satisfaction_score': 7, 'attended': True, 'outcome': 'Progress'}
        ],
        'payment_history': [
            {'date': '2024-12-01', 'amount': 500, 'status': 'paid_on_time'},
            {'date': '2024-11-01', 'amount': 500, 'status': 'paid_on_time'}
        ],
        'action_items': [
            {'due_date': '2024-12-10', 'status': 'completed'},
            {'due_date': '2024-12-15', 'status': 'in_progress'},
            {'due_date': '2024-11-30', 'status': 'completed'}
        ],
        'communication_log': [
            {'date': '2024-12-06', 'response_time_hours': 4, 'initiated_by': 'client'},
            {'date': '2024-12-01', 'response_time_hours': 12, 'initiated_by': 'coach'}
        ],
        'goal_progress': {'percentage': 75}
    }
    
    async def test_health_assessment():
        # You would pass actual OpenAI API key here
        result = await assess_client_health_intelligence(test_client, 'test-api-key')
        print(json.dumps(result, indent=2))
    
    # asyncio.run(test_health_assessment())  # Uncomment to test