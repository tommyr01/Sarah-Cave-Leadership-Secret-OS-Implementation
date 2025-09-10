"""
Business Intelligence automation for Sarah Cave's Leadership Secret Operating System.
Generates executive dashboard feeds and analytics for real-time business insights.
"""

from typing import Dict, Any, List, Optional, Tuple
import openai
import json
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from dataclasses import dataclass

class MetricType(str, Enum):
    REVENUE = "Revenue"
    CLIENT_COUNT = "Client Count"
    LEAD_CONVERSION = "Lead Conversion"
    SESSION_UTILIZATION = "Session Utilization"
    CLIENT_SATISFACTION = "Client Satisfaction"
    ASSOCIATE_PERFORMANCE = "Associate Performance"

class DashboardWidget(str, Enum):
    PIPELINE_SUMMARY = "Pipeline Summary"
    REVENUE_FORECAST = "Revenue Forecast"
    CLIENT_HEALTH_ALERTS = "Client Health Alerts"
    LEAD_FUNNEL = "Lead Funnel"
    SESSION_ACTIVITY = "Session Activity"
    ASSOCIATE_METRICS = "Associate Metrics"
    FINANCIAL_KPIs = "Financial KPIs"

@dataclass
class BusinessMetric:
    name: str
    current_value: float
    previous_value: float
    target_value: float
    trend_direction: str  # "up", "down", "stable"
    change_percentage: float
    formatted_display: str
    alert_level: str  # "normal", "warning", "critical"

class BusinessIntelligenceEngine:
    """
    AI-powered business intelligence engine for Sarah Cave's coaching business.
    Generates real-time dashboard feeds and executive analytics.
    """
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.analytics_prompt = self._get_analytics_prompt()
    
    def _get_analytics_prompt(self) -> str:
        """System prompt for business intelligence AI analysis."""
        return """
You are an expert business intelligence analyst for Sarah Cave's executive coaching business. Your role is to analyze business data and provide actionable insights for strategic decision-making.

Core Competencies:
1. Transform raw business data into executive-level insights
2. Identify trends, patterns, and anomalies in coaching business metrics
3. Generate forecasts and recommendations based on historical performance
4. Flag risks and opportunities requiring immediate attention

Your Analysis Framework:
- Revenue Analysis: Monthly recurring revenue, deal pipeline, conversion rates
- Client Metrics: Acquisition, retention, satisfaction, lifetime value
- Operational Efficiency: Session utilization, associate performance, capacity planning
- Lead Intelligence: Source effectiveness, conversion funnel optimization
- Financial Health: Cash flow, profitability, growth trajectory

Key Performance Indicators to Monitor:
- Monthly Recurring Revenue (MRR) and growth rate
- Client Acquisition Cost (CAC) vs Customer Lifetime Value (CLV)
- Lead-to-client conversion rates by source
- Session booking rates and no-show percentages
- Client satisfaction scores and Net Promoter Score
- Associate utilization rates and performance metrics

Output Requirements:
- Executive Summary: 2-3 sentence overview of business health
- Key Metrics: Current values, trends, and target comparisons
- Risk Alerts: Issues requiring immediate attention
- Growth Opportunities: Data-driven recommendations for scaling
- Forecasts: 30/60/90-day projections based on current trends

Analysis Constraints:
- Focus on actionable insights over raw data reporting
- Prioritize metrics that directly impact revenue and client satisfaction
- Flag any data inconsistencies or quality issues
- Provide confidence levels for forecasts and recommendations
"""

    async def generate_executive_dashboard_intelligence(
        self, 
        business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive executive dashboard with AI-powered insights.
        
        Args:
            business_data: Complete business metrics from all Airtable tables
                - clients: Client data with health scores and satisfaction
                - sessions: Session history and utilization metrics
                - leads: Lead pipeline and conversion data
                - deals: Revenue pipeline and forecasting data
                - associates: Team performance and capacity metrics
                - invoices: Financial performance and cash flow
                - action_items: Operational efficiency metrics
        
        Returns:
            Executive dashboard data with AI insights and recommendations
        """
        
        # Calculate core business metrics
        revenue_metrics = self._calculate_revenue_metrics(business_data)
        client_metrics = self._calculate_client_metrics(business_data)
        operational_metrics = self._calculate_operational_metrics(business_data)
        lead_metrics = self._calculate_lead_metrics(business_data)
        
        # Prepare comprehensive business context for AI analysis
        business_context = self._prepare_business_context(
            revenue_metrics, client_metrics, operational_metrics, lead_metrics
        )
        
        try:
            # Get AI-powered business insights
            ai_insights = await self._get_ai_business_insights(business_context)
            
            # Generate dashboard widgets
            dashboard_widgets = await self._generate_dashboard_widgets(
                business_data, ai_insights
            )
            
            # Calculate health scores and alerts
            business_health = self._assess_business_health(
                revenue_metrics, client_metrics, operational_metrics
            )
            
            return {
                'executive_summary': ai_insights.get('executive_summary', ''),
                'business_health_score': business_health['overall_score'],
                'health_status': business_health['status'],
                'key_metrics': {
                    'revenue': revenue_metrics,
                    'clients': client_metrics,
                    'operations': operational_metrics,
                    'leads': lead_metrics
                },
                'dashboard_widgets': dashboard_widgets,
                'alerts': business_health['alerts'],
                'recommendations': ai_insights.get('recommendations', []),
                'forecasts': ai_insights.get('forecasts', {}),
                'generated_at': datetime.utcnow().isoformat(),
                'next_update': (datetime.utcnow() + timedelta(hours=6)).isoformat()
            }
            
        except Exception as e:
            # Fallback to rule-based dashboard generation
            return self._fallback_dashboard_generation(
                revenue_metrics, client_metrics, operational_metrics, lead_metrics, str(e)
            )
    
    def _calculate_revenue_metrics(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive revenue and financial metrics."""
        deals = business_data.get('deals', [])
        invoices = business_data.get('invoices', [])
        clients = business_data.get('clients', [])
        
        # Current month calculations
        current_month = datetime.now().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Monthly Recurring Revenue calculation
        active_clients = [c for c in clients if c.get('status') == 'Active']
        current_mrr = sum(float(c.get('monthly_fee', 0)) for c in active_clients)
        
        # Deal pipeline analysis
        open_deals = [d for d in deals if d.get('stage') not in ['Closed Won', 'Closed Lost']]
        pipeline_value = sum(float(d.get('amount', 0)) for d in open_deals)
        
        # Recent closed deals
        recent_deals = [
            d for d in deals 
            if d.get('close_date') and 
            datetime.fromisoformat(d['close_date'].replace('Z', '+00:00')).month == current_month.month
        ]
        monthly_new_revenue = sum(float(d.get('amount', 0)) for d in recent_deals if d.get('stage') == 'Closed Won')
        
        # Invoice analysis
        paid_invoices = [i for i in invoices if i.get('payment_status') == 'Paid']
        current_month_revenue = sum(
            float(i.get('amount', 0)) for i in paid_invoices
            if i.get('invoice_date') and 
            datetime.fromisoformat(i['invoice_date'].replace('Z', '+00:00')).month == current_month.month
        )
        
        # Growth calculations
        previous_month_clients = len([c for c in clients if c.get('start_date') and 
                                    datetime.fromisoformat(c['start_date'].replace('Z', '+00:00')) < current_month])
        client_growth = len(active_clients) - previous_month_clients if previous_month_clients > 0 else 0
        
        return {
            'monthly_recurring_revenue': current_mrr,
            'pipeline_value': pipeline_value,
            'monthly_new_revenue': monthly_new_revenue,
            'current_month_revenue': current_month_revenue,
            'active_client_count': len(active_clients),
            'client_growth': client_growth,
            'average_deal_size': pipeline_value / max(len(open_deals), 1),
            'revenue_per_client': current_mrr / max(len(active_clients), 1)
        }
    
    def _calculate_client_metrics(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate client satisfaction and retention metrics."""
        clients = business_data.get('clients', [])
        sessions = business_data.get('sessions', [])
        
        # Client health analysis
        healthy_clients = len([c for c in clients if c.get('health_score', 0) >= 80])
        at_risk_clients = len([c for c in clients if 60 <= c.get('health_score', 0) < 80])
        critical_clients = len([c for c in clients if c.get('health_score', 0) < 60])
        
        # Satisfaction scoring
        recent_sessions = [
            s for s in sessions 
            if s.get('session_date') and 
            datetime.fromisoformat(s['session_date'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=30)
        ]
        
        satisfaction_scores = [
            float(s.get('satisfaction_rating', 0)) for s in recent_sessions 
            if s.get('satisfaction_rating')
        ]
        avg_satisfaction = sum(satisfaction_scores) / max(len(satisfaction_scores), 1)
        
        # Client lifecycle analysis
        new_clients_30d = len([
            c for c in clients 
            if c.get('start_date') and 
            datetime.fromisoformat(c['start_date'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=30)
        ])
        
        # Session frequency analysis
        total_sessions = len([s for s in sessions if s.get('status') == 'Completed'])
        active_clients = len([c for c in clients if c.get('status') == 'Active'])
        avg_sessions_per_client = total_sessions / max(active_clients, 1)
        
        return {
            'total_clients': len(clients),
            'active_clients': active_clients,
            'healthy_clients': healthy_clients,
            'at_risk_clients': at_risk_clients,
            'critical_clients': critical_clients,
            'average_satisfaction': round(avg_satisfaction, 2),
            'new_clients_30d': new_clients_30d,
            'avg_sessions_per_client': round(avg_sessions_per_client, 1),
            'client_health_distribution': {
                'healthy': healthy_clients,
                'at_risk': at_risk_clients,
                'critical': critical_clients
            }
        }
    
    def _calculate_operational_metrics(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate operational efficiency and associate performance metrics."""
        sessions = business_data.get('sessions', [])
        associates = business_data.get('associates', [])
        action_items = business_data.get('action_items', [])
        
        # Session utilization
        scheduled_sessions = [s for s in sessions if s.get('status') in ['Scheduled', 'Completed']]
        completed_sessions = [s for s in sessions if s.get('status') == 'Completed']
        no_shows = [s for s in sessions if s.get('status') == 'No Show']
        
        completion_rate = len(completed_sessions) / max(len(scheduled_sessions), 1)
        no_show_rate = len(no_shows) / max(len(scheduled_sessions), 1)
        
        # Associate performance
        active_associates = [a for a in associates if a.get('status') == 'Active']
        associate_utilization = {}
        
        for associate in active_associates:
            associate_sessions = [
                s for s in sessions 
                if s.get('associate_id') == associate.get('id') and s.get('status') == 'Completed'
            ]
            utilization = len(associate_sessions) / max(associate.get('monthly_capacity', 1), 1)
            associate_utilization[associate.get('name', 'Unknown')] = round(utilization, 2)
        
        # Action item completion
        completed_actions = [a for a in action_items if a.get('status') == 'Complete']
        overdue_actions = [
            a for a in action_items 
            if a.get('due_date') and a.get('status') != 'Complete' and
            datetime.fromisoformat(a['due_date'].replace('Z', '+00:00')) < datetime.now()
        ]
        
        action_completion_rate = len(completed_actions) / max(len(action_items), 1)
        
        return {
            'session_completion_rate': round(completion_rate * 100, 1),
            'no_show_rate': round(no_show_rate * 100, 1),
            'total_sessions_completed': len(completed_sessions),
            'active_associates': len(active_associates),
            'associate_utilization': associate_utilization,
            'avg_associate_utilization': round(sum(associate_utilization.values()) / max(len(associate_utilization), 1), 2),
            'action_completion_rate': round(action_completion_rate * 100, 1),
            'overdue_actions': len(overdue_actions)
        }
    
    def _calculate_lead_metrics(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate lead generation and conversion metrics."""
        leads = business_data.get('leads', [])
        deals = business_data.get('deals', [])
        
        # Lead source analysis
        lead_sources = {}
        for lead in leads:
            source = lead.get('lead_source', 'Unknown')
            lead_sources[source] = lead_sources.get(source, 0) + 1
        
        # Conversion analysis
        converted_leads = [l for l in leads if l.get('status') == 'Converted']
        qualified_leads = [l for l in leads if l.get('lead_score', 0) >= 70]
        
        conversion_rate = len(converted_leads) / max(len(leads), 1)
        qualification_rate = len(qualified_leads) / max(len(leads), 1)
        
        # Recent lead activity
        recent_leads = [
            l for l in leads 
            if l.get('created_date') and 
            datetime.fromisoformat(l['created_date'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=30)
        ]
        
        # Lead scoring distribution
        hot_leads = len([l for l in leads if l.get('lead_score', 0) >= 80])
        warm_leads = len([l for l in leads if 60 <= l.get('lead_score', 0) < 80])
        cold_leads = len([l for l in leads if l.get('lead_score', 0) < 60])
        
        return {
            'total_leads': len(leads),
            'recent_leads_30d': len(recent_leads),
            'qualified_leads': len(qualified_leads),
            'converted_leads': len(converted_leads),
            'conversion_rate': round(conversion_rate * 100, 1),
            'qualification_rate': round(qualification_rate * 100, 1),
            'lead_sources': lead_sources,
            'lead_scoring_distribution': {
                'hot': hot_leads,
                'warm': warm_leads,
                'cold': cold_leads
            },
            'top_lead_source': max(lead_sources.items(), key=lambda x: x[1])[0] if lead_sources else 'None'
        }
    
    def _prepare_business_context(
        self, 
        revenue_metrics: Dict[str, Any],
        client_metrics: Dict[str, Any], 
        operational_metrics: Dict[str, Any],
        lead_metrics: Dict[str, Any]
    ) -> str:
        """Prepare comprehensive business context for AI analysis."""
        
        context_parts = [
            "=== SARAH CAVE COACHING BUSINESS INTELLIGENCE REPORT ===",
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "REVENUE METRICS:",
            f"- Monthly Recurring Revenue: ${revenue_metrics['monthly_recurring_revenue']:,.2f}",
            f"- Pipeline Value: ${revenue_metrics['pipeline_value']:,.2f}",
            f"- Monthly New Revenue: ${revenue_metrics['monthly_new_revenue']:,.2f}",
            f"- Active Clients: {revenue_metrics['active_client_count']}",
            f"- Client Growth: {revenue_metrics['client_growth']:+d}",
            f"- Average Deal Size: ${revenue_metrics['average_deal_size']:,.2f}",
            "",
            "CLIENT HEALTH METRICS:",
            f"- Total Clients: {client_metrics['total_clients']}",
            f"- Healthy Clients: {client_metrics['healthy_clients']} ({client_metrics['healthy_clients']/max(client_metrics['total_clients'], 1)*100:.1f}%)",
            f"- At Risk Clients: {client_metrics['at_risk_clients']}",
            f"- Critical Clients: {client_metrics['critical_clients']}",
            f"- Average Satisfaction: {client_metrics['average_satisfaction']}/10",
            f"- New Clients (30d): {client_metrics['new_clients_30d']}",
            "",
            "OPERATIONAL EFFICIENCY:",
            f"- Session Completion Rate: {operational_metrics['session_completion_rate']}%",
            f"- No-Show Rate: {operational_metrics['no_show_rate']}%",
            f"- Sessions Completed: {operational_metrics['total_sessions_completed']}",
            f"- Active Associates: {operational_metrics['active_associates']}",
            f"- Avg Associate Utilization: {operational_metrics['avg_associate_utilization']*100:.1f}%",
            f"- Action Completion Rate: {operational_metrics['action_completion_rate']}%",
            "",
            "LEAD GENERATION:",
            f"- Total Leads: {lead_metrics['total_leads']}",
            f"- Recent Leads (30d): {lead_metrics['recent_leads_30d']}",
            f"- Conversion Rate: {lead_metrics['conversion_rate']}%",
            f"- Qualification Rate: {lead_metrics['qualification_rate']}%",
            f"- Top Lead Source: {lead_metrics['top_lead_source']}"
        ]
        
        return "\n".join(context_parts)
    
    async def _get_ai_business_insights(self, business_context: str) -> Dict[str, Any]:
        """Get AI-powered business insights and recommendations."""
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.analytics_prompt},
                    {"role": "user", "content": f"Analyze this business data and provide executive insights:\n\n{business_context}"}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse AI response into structured insights
            insights = self._parse_ai_insights(ai_response)
            
            return insights
            
        except Exception as e:
            return {
                'executive_summary': f"Analysis unavailable due to service error: {str(e)}",
                'recommendations': ["Review system connectivity and retry analysis"],
                'forecasts': {},
                'ai_error': True
            }
    
    def _parse_ai_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured insights."""
        
        # Extract executive summary (first paragraph)
        lines = ai_response.split('\n')
        executive_summary = ""
        recommendations = []
        forecasts = {}
        
        current_section = "summary"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify section headers
            if any(header in line.lower() for header in ['recommendation', 'suggest', 'should']):
                current_section = "recommendations"
            elif any(header in line.lower() for header in ['forecast', 'predict', 'expect']):
                current_section = "forecasts"
            
            # Parse content by section
            if current_section == "summary" and not executive_summary:
                executive_summary = line
            elif current_section == "recommendations" and line:
                if not any(header in line.lower() for header in ['recommendation', 'suggest']):
                    recommendations.append(line.lstrip('- •').strip())
            elif current_section == "forecasts" and line:
                if "30 day" in line.lower() or "month" in line.lower():
                    forecasts['30_day'] = line.lstrip('- •').strip()
        
        return {
            'executive_summary': executive_summary or "Business metrics analyzed successfully.",
            'recommendations': recommendations or ["Continue monitoring key performance indicators"],
            'forecasts': forecasts or {'30_day': 'Forecast data processing'},
            'confidence_level': 'moderate'
        }
    
    async def _generate_dashboard_widgets(
        self, 
        business_data: Dict[str, Any], 
        ai_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for all executive dashboard widgets."""
        
        clients = business_data.get('clients', [])
        sessions = business_data.get('sessions', [])
        leads = business_data.get('leads', [])
        deals = business_data.get('deals', [])
        
        # Pipeline Summary Widget
        pipeline_summary = {
            'total_pipeline_value': sum(float(d.get('amount', 0)) for d in deals if d.get('stage') not in ['Closed Won', 'Closed Lost']),
            'deals_by_stage': self._group_deals_by_stage(deals),
            'conversion_trends': self._calculate_conversion_trends(leads, deals)
        }
        
        # Client Health Alerts Widget
        health_alerts = [
            {
                'client_name': c.get('name', 'Unknown'),
                'health_score': c.get('health_score', 0),
                'risk_category': 'Critical' if c.get('health_score', 0) < 60 else 'At Risk',
                'last_session': c.get('last_session_date', ''),
                'recommended_action': 'Immediate intervention required' if c.get('health_score', 0) < 60 else 'Schedule check-in'
            }
            for c in clients if c.get('health_score', 0) < 80
        ]
        
        # Recent Activity Widget
        recent_activity = [
            {
                'type': 'session',
                'description': f"Session with {s.get('client_name', 'Client')}",
                'date': s.get('session_date', ''),
                'status': s.get('status', '')
            }
            for s in sessions[-10:]  # Last 10 sessions
        ]
        
        # Financial KPIs Widget
        financial_kpis = {
            'mrr_growth': self._calculate_mrr_growth(business_data),
            'revenue_forecast': ai_insights.get('forecasts', {}).get('30_day', 'Calculating...'),
            'client_acquisition_cost': self._calculate_client_acquisition_cost(business_data),
            'lifetime_value': self._calculate_average_lifetime_value(business_data)
        }
        
        return {
            'pipeline_summary': pipeline_summary,
            'client_health_alerts': health_alerts[:5],  # Top 5 alerts
            'recent_activity': recent_activity,
            'financial_kpis': financial_kpis,
            'lead_funnel': self._generate_lead_funnel_data(leads),
            'associate_performance': self._generate_associate_performance_data(business_data)
        }
    
    def _group_deals_by_stage(self, deals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group deals by pipeline stage."""
        stage_counts = {}
        for deal in deals:
            stage = deal.get('stage', 'Unknown')
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        return stage_counts
    
    def _calculate_conversion_trends(self, leads: List[Dict[str, Any]], deals: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate lead to deal conversion trends."""
        
        # Simple conversion calculation
        total_leads = len(leads)
        total_deals = len([d for d in deals if d.get('stage') == 'Closed Won'])
        
        conversion_rate = (total_deals / max(total_leads, 1)) * 100
        
        return {
            'overall_conversion': round(conversion_rate, 2),
            'trend': 'stable'  # Could be enhanced with historical data
        }
    
    def _calculate_mrr_growth(self, business_data: Dict[str, Any]) -> float:
        """Calculate Monthly Recurring Revenue growth rate."""
        clients = business_data.get('clients', [])
        
        # Current MRR
        current_mrr = sum(float(c.get('monthly_fee', 0)) for c in clients if c.get('status') == 'Active')
        
        # Previous month MRR (simplified - would need historical data for accuracy)
        # Using client count as proxy for growth
        total_clients = len([c for c in clients if c.get('status') == 'Active'])
        new_clients = len([
            c for c in clients 
            if c.get('start_date') and 
            datetime.fromisoformat(c['start_date'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=30)
        ])
        
        growth_rate = (new_clients / max(total_clients - new_clients, 1)) * 100 if total_clients > new_clients else 0
        
        return round(growth_rate, 2)
    
    def _calculate_client_acquisition_cost(self, business_data: Dict[str, Any]) -> float:
        """Calculate average Client Acquisition Cost."""
        # Simplified calculation - would need marketing spend data
        leads = business_data.get('leads', [])
        clients = business_data.get('clients', [])
        
        # Assuming basic acquisition cost based on lead volume
        new_clients = len([c for c in clients if c.get('start_date') and 
                         datetime.fromisoformat(c['start_date'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=90)])
        
        # Estimated CAC (would need actual marketing spend)
        estimated_cac = 500.0  # Placeholder - replace with actual calculation
        
        return estimated_cac
    
    def _calculate_average_lifetime_value(self, business_data: Dict[str, Any]) -> float:
        """Calculate average Customer Lifetime Value."""
        clients = business_data.get('clients', [])
        
        if not clients:
            return 0.0
        
        # Calculate average monthly fee
        active_clients = [c for c in clients if c.get('status') == 'Active']
        avg_monthly_fee = sum(float(c.get('monthly_fee', 0)) for c in active_clients) / max(len(active_clients), 1)
        
        # Estimate average client lifespan (12 months as baseline for coaching)
        estimated_lifespan_months = 12
        
        return round(avg_monthly_fee * estimated_lifespan_months, 2)
    
    def _generate_lead_funnel_data(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate lead funnel visualization data."""
        
        total_leads = len(leads)
        qualified_leads = len([l for l in leads if l.get('lead_score', 0) >= 70])
        converted_leads = len([l for l in leads if l.get('status') == 'Converted'])
        
        return {
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'converted_leads': converted_leads,
            'qualification_rate': round((qualified_leads / max(total_leads, 1)) * 100, 1),
            'conversion_rate': round((converted_leads / max(total_leads, 1)) * 100, 1)
        }
    
    def _generate_associate_performance_data(self, business_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate associate performance dashboard data."""
        
        associates = business_data.get('associates', [])
        sessions = business_data.get('sessions', [])
        
        performance_data = []
        
        for associate in associates:
            if associate.get('status') != 'Active':
                continue
                
            associate_sessions = [
                s for s in sessions 
                if s.get('associate_id') == associate.get('id') and s.get('status') == 'Completed'
            ]
            
            # Calculate satisfaction from sessions
            satisfaction_scores = [
                float(s.get('satisfaction_rating', 0)) for s in associate_sessions 
                if s.get('satisfaction_rating')
            ]
            avg_satisfaction = sum(satisfaction_scores) / max(len(satisfaction_scores), 1)
            
            performance_data.append({
                'name': associate.get('name', 'Unknown'),
                'sessions_completed': len(associate_sessions),
                'utilization_rate': round((len(associate_sessions) / max(associate.get('monthly_capacity', 1), 1)) * 100, 1),
                'avg_satisfaction': round(avg_satisfaction, 2),
                'status': 'On Track' if len(associate_sessions) > 0 else 'Low Activity'
            })
        
        return performance_data
    
    def _assess_business_health(
        self, 
        revenue_metrics: Dict[str, Any],
        client_metrics: Dict[str, Any], 
        operational_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall business health and generate alerts."""
        
        health_score = 0
        max_score = 100
        alerts = []
        
        # Revenue health (40 points)
        if revenue_metrics['monthly_recurring_revenue'] > 10000:
            health_score += 40
        elif revenue_metrics['monthly_recurring_revenue'] > 5000:
            health_score += 30
        elif revenue_metrics['monthly_recurring_revenue'] > 2000:
            health_score += 20
        else:
            alerts.append({
                'type': 'revenue',
                'priority': 'high',
                'message': f"Low MRR: ${revenue_metrics['monthly_recurring_revenue']:,.2f}",
                'recommendation': 'Focus on client acquisition and retention'
            })
            health_score += 10
        
        # Client health (30 points)
        if client_metrics['critical_clients'] == 0:
            health_score += 30
        elif client_metrics['critical_clients'] <= 2:
            health_score += 20
            alerts.append({
                'type': 'client_health',
                'priority': 'medium',
                'message': f"{client_metrics['critical_clients']} clients in critical condition",
                'recommendation': 'Schedule immediate intervention sessions'
            })
        else:
            health_score += 10
            alerts.append({
                'type': 'client_health',
                'priority': 'high',
                'message': f"{client_metrics['critical_clients']} clients in critical condition",
                'recommendation': 'Urgent: Develop client retention strategy'
            })
        
        # Operational efficiency (30 points)
        if operational_metrics['session_completion_rate'] >= 90:
            health_score += 30
        elif operational_metrics['session_completion_rate'] >= 80:
            health_score += 20
        else:
            health_score += 10
            alerts.append({
                'type': 'operations',
                'priority': 'medium',
                'message': f"Low session completion: {operational_metrics['session_completion_rate']}%",
                'recommendation': 'Investigate scheduling and no-show issues'
            })
        
        # Determine health status
        if health_score >= 80:
            status = 'Healthy'
        elif health_score >= 60:
            status = 'Stable'
        else:
            status = 'At Risk'
        
        return {
            'overall_score': health_score,
            'status': status,
            'alerts': alerts,
            'assessment_date': datetime.utcnow().isoformat()
        }
    
    def _fallback_dashboard_generation(
        self, 
        revenue_metrics: Dict[str, Any],
        client_metrics: Dict[str, Any], 
        operational_metrics: Dict[str, Any],
        lead_metrics: Dict[str, Any], 
        error: str
    ) -> Dict[str, Any]:
        """Fallback dashboard generation when AI service fails."""
        
        business_health = self._assess_business_health(revenue_metrics, client_metrics, operational_metrics)
        
        return {
            'executive_summary': f'Business dashboard generated with rule-based analysis. AI insights temporarily unavailable: {error}',
            'business_health_score': business_health['overall_score'],
            'health_status': business_health['status'],
            'key_metrics': {
                'revenue': revenue_metrics,
                'clients': client_metrics,
                'operations': operational_metrics,
                'leads': lead_metrics
            },
            'dashboard_widgets': {
                'pipeline_summary': {'note': 'Basic metrics available'},
                'client_health_alerts': business_health['alerts'],
                'financial_kpis': {
                    'mrr': revenue_metrics['monthly_recurring_revenue'],
                    'pipeline': revenue_metrics['pipeline_value']
                }
            },
            'alerts': business_health['alerts'],
            'recommendations': [
                'Review business metrics manually',
                'Check AI service connectivity',
                'Monitor client health scores'
            ],
            'forecasts': {'note': 'AI forecasts unavailable'},
            'generated_at': datetime.utcnow().isoformat(),
            'next_update': (datetime.utcnow() + timedelta(hours=6)).isoformat(),
            'fallback_used': True
        }

# Public interface functions for webhook integration
async def generate_executive_dashboard_intelligence(
    business_data: Dict[str, Any], 
    openai_api_key: str
) -> Dict[str, Any]:
    """
    Main function for generating executive dashboard - called by webhook automation.
    
    Args:
        business_data: Complete business data from all Airtable tables
        openai_api_key: OpenAI API key for AI analysis
    
    Returns:
        Executive dashboard with business intelligence insights
    """
    engine = BusinessIntelligenceEngine(openai_api_key)
    return await engine.generate_executive_dashboard_intelligence(business_data)

async def generate_daily_business_report(
    business_data: Dict[str, Any], 
    openai_api_key: str
) -> Dict[str, Any]:
    """
    Generate daily business report for Sarah's morning review.
    
    Args:
        business_data: Business metrics from previous 24 hours
        openai_api_key: OpenAI API key
    
    Returns:
        Daily business intelligence report
    """
    engine = BusinessIntelligenceEngine(openai_api_key)
    dashboard = await engine.generate_executive_dashboard_intelligence(business_data)
    
    # Format for daily report
    return {
        'report_type': 'daily_business_summary',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'executive_summary': dashboard['executive_summary'],
        'key_alerts': [alert for alert in dashboard['alerts'] if alert['priority'] == 'high'],
        'daily_metrics': {
            'new_leads': business_data.get('daily_new_leads', 0),
            'sessions_completed': len([s for s in business_data.get('sessions', []) if s.get('status') == 'Completed']),
            'revenue_generated': sum(float(i.get('amount', 0)) for i in business_data.get('invoices', []) if i.get('payment_status') == 'Paid'),
            'client_health_changes': len([c for c in business_data.get('clients', []) if c.get('health_score_changed', False)])
        },
        'priority_actions': dashboard['recommendations'][:3],
        'next_report': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'dashboard_url': 'https://airtable.com/sarah-cave-executive-dashboard'
    }

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test business data
    test_business_data = {
        'clients': [
            {'id': '1', 'name': 'John CEO', 'status': 'Active', 'monthly_fee': 2500, 'health_score': 85},
            {'id': '2', 'name': 'Jane CFO', 'status': 'Active', 'monthly_fee': 3000, 'health_score': 45}
        ],
        'sessions': [
            {'client_id': '1', 'status': 'Completed', 'satisfaction_rating': 9, 'session_date': '2025-09-08'},
            {'client_id': '2', 'status': 'Completed', 'satisfaction_rating': 6, 'session_date': '2025-09-07'}
        ],
        'leads': [
            {'lead_source': 'LinkedIn', 'lead_score': 85, 'status': 'Qualified'},
            {'lead_source': 'Referral', 'lead_score': 92, 'status': 'Converted'}
        ],
        'deals': [
            {'amount': 15000, 'stage': 'Proposal', 'close_date': '2025-09-15'},
            {'amount': 18000, 'stage': 'Closed Won', 'close_date': '2025-09-01'}
        ]
    }
    
    async def test_dashboard_generation():
        # You would pass actual OpenAI API key here
        result = await generate_executive_dashboard_intelligence(test_business_data, 'test-api-key')
        print(json.dumps(result, indent=2))
    
    # asyncio.run(test_dashboard_generation())  # Uncomment to test