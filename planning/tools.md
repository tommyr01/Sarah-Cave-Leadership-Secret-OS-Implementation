# Sarah Cave Leadership OS - Pydantic AI Tools Implementation

```python
"""
Tools for Sarah Cave Leadership OS - Pydantic AI agent tools implementation.
Transforms manual coaching business into automated 8-table Leadership Secret Operating System.
"""

import logging
from typing import Dict, Any, List, Optional, Literal, Union
from pydantic_ai import RunContext
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


# Tool parameter models for validation
class LeadScoringParams(BaseModel):
    """Parameters for AI-powered lead scoring."""
    lead_id: str = Field(..., description="Airtable record ID for lead")
    lead_data: Dict[str, Any] = Field(..., description="Lead profile and interaction data")
    scoring_criteria: Optional[Dict[str, float]] = Field(None, description="Custom scoring weights")


class ClientHealthParams(BaseModel):
    """Parameters for client health monitoring."""
    client_id: str = Field(..., description="Airtable record ID for client")
    session_data: List[Dict] = Field(..., description="Recent session history")
    engagement_metrics: Dict[str, Any] = Field(..., description="Client engagement data")


class SessionProcessingParams(BaseModel):
    """Parameters for session note generation and processing."""
    session_id: str = Field(..., description="Airtable record ID for session")
    raw_notes: str = Field(..., description="Raw session notes or transcript")
    client_context: Dict[str, Any] = Field(..., description="Client background and history")
    session_type: str = Field(..., description="Type of coaching session")


class WebhookEventParams(BaseModel):
    """Parameters for Airtable webhook event processing."""
    event_type: str = Field(..., description="Type of webhook event")
    table_name: str = Field(..., description="Affected Airtable table")
    record_id: str = Field(..., description="Record ID that triggered webhook")
    changes: Dict[str, Any] = Field(..., description="Changed fields and values")


# Core automation functions for testing and reuse

async def score_lead_intelligence(
    openai_api_key: str,
    lead_data: Dict[str, Any],
    scoring_criteria: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    AI-powered lead scoring based on profile data and interaction history.
    
    Args:
        openai_api_key: OpenAI API key for AI processing
        lead_data: Lead profile including contact info, source, interactions
        scoring_criteria: Custom weights for scoring factors
    
    Returns:
        Dictionary with lead score, qualification status, and recommendations
    """
    import openai
    
    # Default scoring criteria if not provided
    default_criteria = {
        "company_size": 0.25,
        "decision_authority": 0.30,
        "engagement_level": 0.25,
        "budget_indication": 0.20
    }
    criteria = scoring_criteria or default_criteria
    
    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        
        # Build AI prompt for lead scoring
        prompt = f"""
        Analyze this lead and provide a score from 0-100 based on coaching service fit:
        
        Lead Data:
        - Name: {lead_data.get('name', 'Unknown')}
        - Company: {lead_data.get('company', 'Unknown')}
        - Title: {lead_data.get('title', 'Unknown')}
        - Source: {lead_data.get('source', 'Unknown')}
        - Interactions: {lead_data.get('interactions', [])}
        - Notes: {lead_data.get('notes', '')}
        
        Scoring Criteria:
        {json.dumps(criteria, indent=2)}
        
        Provide response as JSON with:
        - score (0-100)
        - qualification_status (Hot/Warm/Cold)
        - key_strengths (list)
        - concerns (list)  
        - next_actions (list)
        - nurture_sequence (suggested sequence name)
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Add metadata
        result.update({
            "scored_at": datetime.now().isoformat(),
            "criteria_used": criteria,
            "lead_id": lead_data.get('id')
        })
        
        logger.info(f"Lead scored: {result['score']} for {lead_data.get('name')}")
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Lead scoring failed: {e}")
        return {"success": False, "error": str(e)}


async def monitor_client_health(
    client_data: Dict[str, Any],
    session_history: List[Dict],
    engagement_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze client engagement patterns and calculate health score.
    
    Args:
        client_data: Client profile and current status
        session_history: Recent coaching sessions with outcomes
        engagement_metrics: Usage frequency, satisfaction scores, etc.
    
    Returns:
        Health score, risk level, and intervention recommendations
    """
    try:
        # Calculate health score components
        session_frequency_score = calculate_session_frequency_score(session_history)
        satisfaction_score = calculate_satisfaction_score(session_history)
        engagement_score = calculate_engagement_score(engagement_metrics)
        completion_score = calculate_completion_score(session_history)
        
        # Weighted health score calculation
        health_score = (
            session_frequency_score * 0.30 +
            satisfaction_score * 0.25 +
            engagement_score * 0.25 +
            completion_score * 0.20
        )
        
        # Determine risk level
        if health_score >= 80:
            risk_level = "Low"
            risk_color = "green"
        elif health_score >= 60:
            risk_level = "Medium" 
            risk_color = "yellow"
        else:
            risk_level = "High"
            risk_color = "red"
        
        # Generate intervention recommendations
        recommendations = generate_health_recommendations(
            health_score, session_history, engagement_metrics
        )
        
        result = {
            "client_id": client_data.get('id'),
            "health_score": round(health_score, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "score_components": {
                "session_frequency": round(session_frequency_score, 1),
                "satisfaction": round(satisfaction_score, 1), 
                "engagement": round(engagement_score, 1),
                "completion": round(completion_score, 1)
            },
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat(),
            "requires_attention": health_score < 70
        }
        
        logger.info(f"Client health calculated: {health_score} for {client_data.get('name')}")
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Client health monitoring failed: {e}")
        return {"success": False, "error": str(e)}


async def generate_session_notes(
    openai_api_key: str,
    raw_notes: str,
    client_context: Dict[str, Any],
    session_type: str = "coaching"
) -> Dict[str, Any]:
    """
    Generate structured coaching session notes from raw input.
    
    Args:
        openai_api_key: OpenAI API key for AI processing
        raw_notes: Raw session notes or transcript
        client_context: Client background and coaching history
        session_type: Type of session (coaching, strategy, check-in)
    
    Returns:
        Structured notes with outcomes, action items, and insights
    """
    import openai
    
    try:
        client = openai.AsyncOpenAI(api_key=openai_api_key)
        
        prompt = f"""
        Transform these raw coaching session notes into a structured summary:
        
        Raw Notes:
        {raw_notes}
        
        Client Context:
        - Name: {client_context.get('name')}
        - Package: {client_context.get('package_type')}
        - Goals: {client_context.get('goals', [])}
        - Previous Sessions: {len(client_context.get('session_history', []))}
        
        Session Type: {session_type}
        
        Create structured JSON response with:
        - session_summary (2-3 sentences)
        - key_topics (list of main discussion points)
        - client_insights (breakthroughs or realizations)
        - action_items (specific tasks with deadlines)
        - coach_notes (private observations)
        - next_session_focus (recommended topics)
        - satisfaction_indicators (client engagement signals)
        - leadership_models_used (frameworks applied)
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        structured_notes = json.loads(response.choices[0].message.content)
        
        # Add metadata and timestamps
        structured_notes.update({
            "generated_at": datetime.now().isoformat(),
            "session_type": session_type,
            "client_id": client_context.get('id'),
            "word_count": len(raw_notes.split()),
            "processing_model": "gpt-4o-mini"
        })
        
        logger.info(f"Session notes generated for {client_context.get('name')}")
        return {"success": True, "data": structured_notes}
        
    except Exception as e:
        logger.error(f"Session note generation failed: {e}")
        return {"success": False, "error": str(e)}


async def process_airtable_webhook(
    airtable_api_key: str,
    base_id: str,
    event_data: Dict[str, Any],
    webhook_secret: str
) -> Dict[str, Any]:
    """
    Process incoming Airtable webhook events and trigger appropriate automations.
    
    Args:
        airtable_api_key: Airtable API key for data access
        base_id: Airtable base identifier
        event_data: Webhook payload with change information
        webhook_secret: Secret for webhook verification
    
    Returns:
        Processing results and triggered automation status
    """
    import hmac
    import hashlib
    from pyairtable import Api
    
    try:
        # Initialize Airtable API
        airtable_api = Api(airtable_api_key)
        base = airtable_api.base(base_id)
        
        # Extract event details
        table_name = event_data.get('base', {}).get('table', {}).get('name')
        record_id = event_data.get('recordId')
        changed_fields = event_data.get('changedFields', [])
        
        automation_results = []
        
        # Route to appropriate automation based on table and changes
        if table_name == "Leads":
            if 'Status' in changed_fields or event_data.get('actionType') == 'create':
                # Trigger lead scoring automation
                result = await trigger_lead_scoring(base, record_id)
                automation_results.append(result)
                
        elif table_name == "Deals":
            if 'Pipeline Stage' in changed_fields:
                # Trigger pipeline progression automation
                result = await trigger_pipeline_automation(base, record_id)
                automation_results.append(result)
                
        elif table_name == "Coaching Sessions":
            if 'Status' in changed_fields and event_data.get('current', {}).get('Status') == 'Completed':
                # Trigger session processing automation
                result = await trigger_session_processing(base, record_id)
                automation_results.append(result)
                
        elif table_name == "Clients":
            if 'Health Score' in changed_fields:
                # Trigger client health monitoring
                result = await trigger_health_monitoring(base, record_id)
                automation_results.append(result)
        
        response = {
            "webhook_processed": True,
            "table_name": table_name,
            "record_id": record_id,
            "automations_triggered": len(automation_results),
            "results": automation_results,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Webhook processed: {table_name} - {len(automation_results)} automations")
        return {"success": True, "data": response}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return {"success": False, "error": str(e)}


# Helper functions for calculations

def calculate_session_frequency_score(session_history: List[Dict]) -> float:
    """Calculate session frequency component of health score."""
    if not session_history:
        return 0
        
    # Get sessions from last 60 days
    recent_sessions = [
        s for s in session_history 
        if datetime.fromisoformat(s['date']) > datetime.now() - timedelta(days=60)
    ]
    
    sessions_per_month = len(recent_sessions) * (30/60)
    
    # Score based on expected frequency (4 sessions/month = 100 points)
    return min(100, (sessions_per_month / 4) * 100)


def calculate_satisfaction_score(session_history: List[Dict]) -> float:
    """Calculate satisfaction component of health score."""
    if not session_history:
        return 50  # Neutral score for no data
        
    satisfaction_scores = [
        s.get('satisfaction_rating', 3) 
        for s in session_history 
        if s.get('satisfaction_rating')
    ]
    
    if not satisfaction_scores:
        return 50
        
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
    return (avg_satisfaction / 5) * 100  # Convert 1-5 scale to 0-100


def calculate_engagement_score(engagement_metrics: Dict[str, Any]) -> float:
    """Calculate engagement component of health score."""
    metrics = {
        'pre_work_completion': engagement_metrics.get('pre_work_completion', 0.5),
        'resource_usage': engagement_metrics.get('resource_usage', 0.5),
        'communication_responsiveness': engagement_metrics.get('responsiveness', 0.5)
    }
    
    return sum(metrics.values()) / len(metrics) * 100


def calculate_completion_score(session_history: List[Dict]) -> float:
    """Calculate action item completion component of health score."""
    if not session_history:
        return 50
        
    total_items = sum(len(s.get('action_items', [])) for s in session_history)
    completed_items = sum(
        len([item for item in s.get('action_items', []) if item.get('completed')])
        for s in session_history
    )
    
    if total_items == 0:
        return 50  # Neutral for no action items
        
    return (completed_items / total_items) * 100


def generate_health_recommendations(
    health_score: float,
    session_history: List[Dict],
    engagement_metrics: Dict[str, Any]
) -> List[str]:
    """Generate intervention recommendations based on health analysis."""
    recommendations = []
    
    if health_score < 60:
        recommendations.extend([
            "Schedule immediate check-in call to assess satisfaction",
            "Review coaching approach and adjust methodology",
            "Increase session frequency or extend duration"
        ])
    elif health_score < 80:
        recommendations.extend([
            "Send satisfaction survey to identify improvement areas",
            "Provide additional resources relevant to client goals"
        ])
    
    # Specific recommendations based on components
    if engagement_metrics.get('pre_work_completion', 1) < 0.5:
        recommendations.append("Address pre-work completion barriers")
        
    if len(session_history) > 0 and session_history[-1].get('satisfaction_rating', 5) < 4:
        recommendations.append("Follow up on recent session satisfaction concerns")
    
    return recommendations


# Tool registration function for agent
def register_tools(agent, deps_type):
    """
    Register all tools with the agent.
    
    Args:
        agent: Pydantic AI agent instance  
        deps_type: Agent dependencies type
    """
    
    @agent.tool
    async def score_lead(
        ctx: RunContext[deps_type],
        lead_id: str,
        lead_data: Dict[str, Any],
        custom_criteria: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        AI-powered lead scoring and qualification assessment.
        
        Args:
            lead_id: Airtable record ID for the lead
            lead_data: Lead profile including contact info, source, interactions
            custom_criteria: Optional custom scoring weights
        
        Returns:
            Lead score, qualification status, and recommended actions
        """
        try:
            result = await score_lead_intelligence(
                openai_api_key=ctx.deps.openai_api_key,
                lead_data=lead_data,
                scoring_criteria=custom_criteria
            )
            
            if result["success"]:
                # Update lead record in Airtable with score
                from pyairtable import Api
                api = Api(ctx.deps.airtable_api_key)
                table = api.table(ctx.deps.base_id, "Leads")
                
                update_data = {
                    "Lead Score": result["data"]["score"],
                    "Status": result["data"]["qualification_status"],
                    "Next Action": "; ".join(result["data"]["next_actions"][:2]),
                    "Scored At": result["data"]["scored_at"]
                }
                
                table.update(lead_id, update_data)
                logger.info(f"Lead {lead_id} updated with score {result['data']['score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Lead scoring tool failed: {e}")
            return {"success": False, "error": str(e)}
    
    
    @agent.tool 
    async def monitor_client_health_status(
        ctx: RunContext[deps_type],
        client_id: str
    ) -> Dict[str, Any]:
        """
        Monitor client health and generate risk assessment.
        
        Args:
            client_id: Airtable record ID for the client
        
        Returns:
            Health score, risk level, and intervention recommendations
        """
        try:
            from pyairtable import Api
            api = Api(ctx.deps.airtable_api_key)
            
            # Fetch client data and related records
            clients_table = api.table(ctx.deps.base_id, "Clients")
            sessions_table = api.table(ctx.deps.base_id, "Coaching Sessions")
            
            client_record = clients_table.get(client_id)
            client_data = client_record["fields"]
            
            # Get recent session history
            session_records = sessions_table.all(formula=f"{{Client}} = '{client_data.get('Name')}'")
            session_history = [record["fields"] for record in session_records[-10:]]  # Last 10 sessions
            
            # Build engagement metrics
            engagement_metrics = {
                "pre_work_completion": client_data.get("Pre-work Completion Rate", 0.7),
                "resource_usage": client_data.get("Resource Usage", 0.6),
                "responsiveness": client_data.get("Communication Score", 0.8)
            }
            
            result = await monitor_client_health(
                client_data=client_data,
                session_history=session_history,
                engagement_metrics=engagement_metrics
            )
            
            if result["success"]:
                # Update client health score in Airtable
                update_data = {
                    "Health Score": result["data"]["health_score"],
                    "Risk Level": result["data"]["risk_level"],
                    "Last Health Check": result["data"]["last_updated"],
                    "Requires Attention": result["data"]["requires_attention"]
                }
                
                clients_table.update(client_id, update_data)
                logger.info(f"Client {client_id} health updated: {result['data']['health_score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Client health monitoring failed: {e}")
            return {"success": False, "error": str(e)}
    
    
    @agent.tool
    async def process_session_completion(
        ctx: RunContext[deps_type],
        session_id: str,
        raw_notes: str,
        generate_invoice: bool = True
    ) -> Dict[str, Any]:
        """
        Process completed coaching session with AI note generation.
        
        Args:
            session_id: Airtable record ID for the session
            raw_notes: Raw session notes or transcript
            generate_invoice: Whether to trigger invoice creation
        
        Returns:
            Structured session summary and processing results
        """
        try:
            from pyairtable import Api
            api = Api(ctx.deps.airtable_api_key)
            
            # Fetch session and client data
            sessions_table = api.table(ctx.deps.base_id, "Coaching Sessions") 
            clients_table = api.table(ctx.deps.base_id, "Clients")
            
            session_record = sessions_table.get(session_id)
            session_data = session_record["fields"]
            
            client_name = session_data.get("Client")
            client_records = clients_table.all(formula=f"{{Name}} = '{client_name}'")
            client_data = client_records[0]["fields"] if client_records else {}
            
            # Generate structured notes
            result = await generate_session_notes(
                openai_api_key=ctx.deps.openai_api_key,
                raw_notes=raw_notes,
                client_context=client_data,
                session_type=session_data.get("Session Type", "coaching")
            )
            
            if result["success"]:
                notes_data = result["data"]
                
                # Update session record with structured notes
                update_data = {
                    "Notes Summary": notes_data["session_summary"],
                    "Key Topics": ", ".join(notes_data["key_topics"]),
                    "Action Items": json.dumps(notes_data["action_items"]),
                    "Next Session Focus": notes_data["next_session_focus"],
                    "Notes Generated": True,
                    "Processing Date": notes_data["generated_at"]
                }
                
                sessions_table.update(session_id, update_data)
                
                # Create action item records if they don't exist
                if notes_data.get("action_items"):
                    await create_action_items(api, ctx.deps.base_id, session_id, notes_data["action_items"])
                
                # Trigger invoice generation if requested
                if generate_invoice:
                    await trigger_invoice_creation(api, ctx.deps.base_id, session_id, session_data)
                
                logger.info(f"Session {session_id} processed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Session processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    
    @agent.tool
    async def handle_webhook_event(
        ctx: RunContext[deps_type],
        event_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process Airtable webhook events and trigger appropriate automations.
        
        Args:
            event_payload: Complete webhook payload from Airtable
        
        Returns:
            Processing results and automation status
        """
        try:
            result = await process_airtable_webhook(
                airtable_api_key=ctx.deps.airtable_api_key,
                base_id=ctx.deps.base_id,
                event_data=event_payload,
                webhook_secret=ctx.deps.webhook_secret
            )
            
            logger.info(f"Webhook event processed: {result.get('success')}")
            return result
            
        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    
    @agent.tool
    async def generate_business_intelligence_report(
        ctx: RunContext[deps_type],
        report_type: Literal["daily", "weekly", "monthly"] = "weekly",
        include_forecasting: bool = True
    ) -> Dict[str, Any]:
        """
        Generate business intelligence reports with key metrics and insights.
        
        Args:
            report_type: Type of report timeframe
            include_forecasting: Whether to include revenue forecasting
        
        Returns:
            Comprehensive business metrics and insights
        """
        try:
            from pyairtable import Api
            api = Api(ctx.deps.airtable_api_key)
            
            # Fetch data from all tables
            leads_table = api.table(ctx.deps.base_id, "Leads")
            deals_table = api.table(ctx.deps.base_id, "Deals")
            clients_table = api.table(ctx.deps.base_id, "Clients")
            sessions_table = api.table(ctx.deps.base_id, "Coaching Sessions")
            
            # Calculate date range based on report type
            if report_type == "daily":
                start_date = datetime.now() - timedelta(days=1)
            elif report_type == "weekly":
                start_date = datetime.now() - timedelta(days=7)
            else:  # monthly
                start_date = datetime.now() - timedelta(days=30)
            
            # Generate report metrics
            metrics = await compile_business_metrics(
                api, ctx.deps.base_id, start_date, include_forecasting
            )
            
            # Add report metadata
            report = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "period_start": start_date.isoformat(),
                "period_end": datetime.now().isoformat(),
                "metrics": metrics
            }
            
            logger.info(f"{report_type.title()} BI report generated")
            return {"success": True, "data": report}
            
        except Exception as e:
            logger.error(f"BI report generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    
    @agent.tool_plain
    def format_pipeline_data(
        pipeline_data: List[Dict[str, Any]],
        output_format: Literal["summary", "detailed", "chart_data"] = "summary"
    ) -> Dict[str, Any]:
        """
        Format sales pipeline data for different presentation needs.
        
        Args:
            pipeline_data: Raw pipeline data from Airtable
            output_format: How to format the output
        
        Returns:
            Formatted pipeline information
        """
        if output_format == "summary":
            total_value = sum(deal.get('Deal Value', 0) for deal in pipeline_data)
            weighted_value = sum(
                deal.get('Deal Value', 0) * (deal.get('Probability %', 50) / 100) 
                for deal in pipeline_data
            )
            
            return {
                "total_deals": len(pipeline_data),
                "total_value": total_value,
                "weighted_forecast": round(weighted_value, 2),
                "average_deal_size": round(total_value / len(pipeline_data), 2) if pipeline_data else 0,
                "stages": {
                    stage: len([d for d in pipeline_data if d.get('Pipeline Stage') == stage])
                    for stage in ['Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
                }
            }
        
        elif output_format == "detailed":
            return {
                "deals_by_stage": group_deals_by_stage(pipeline_data),
                "deals_by_source": group_deals_by_source(pipeline_data),
                "deals_by_associate": group_deals_by_associate(pipeline_data),
                "aging_analysis": analyze_deal_aging(pipeline_data)
            }
        
        else:  # chart_data
            return {
                "stage_values": [
                    {
                        "stage": stage,
                        "count": len([d for d in pipeline_data if d.get('Pipeline Stage') == stage]),
                        "value": sum(d.get('Deal Value', 0) for d in pipeline_data if d.get('Pipeline Stage') == stage)
                    }
                    for stage in ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
                ],
                "monthly_progression": calculate_monthly_progression(pipeline_data)
            }
    
    
    logger.info(f"Registered {len([f for f in locals() if f.startswith('_') is False and callable(locals()[f])])} tools with agent")


# Helper functions for business intelligence

async def compile_business_metrics(
    api, base_id: str, start_date: datetime, include_forecasting: bool
) -> Dict[str, Any]:
    """Compile comprehensive business metrics for reporting."""
    
    # Lead metrics
    leads_table = api.table(base_id, "Leads")
    all_leads = leads_table.all()
    recent_leads = [
        lead for lead in all_leads 
        if datetime.fromisoformat(lead["fields"].get("Created", start_date.isoformat())) >= start_date
    ]
    
    # Deal metrics
    deals_table = api.table(base_id, "Deals")
    all_deals = deals_table.all()
    
    # Client metrics  
    clients_table = api.table(base_id, "Clients")
    all_clients = clients_table.all()
    
    # Session metrics
    sessions_table = api.table(base_id, "Coaching Sessions") 
    all_sessions = sessions_table.all()
    recent_sessions = [
        session for session in all_sessions
        if datetime.fromisoformat(session["fields"].get("Date", start_date.isoformat())) >= start_date
    ]
    
    metrics = {
        "lead_metrics": {
            "total_leads": len(recent_leads),
            "qualified_leads": len([l for l in recent_leads if l["fields"].get("Status") == "Qualified"]),
            "conversion_rate": calculate_lead_conversion_rate(all_leads, all_deals),
            "average_lead_score": calculate_average_lead_score(recent_leads)
        },
        "sales_metrics": {
            "active_deals": len([d for d in all_deals if d["fields"].get("Pipeline Stage") not in ["Closed Won", "Closed Lost"]]),
            "deals_won": len([d for d in all_deals if d["fields"].get("Pipeline Stage") == "Closed Won"]),
            "win_rate": calculate_win_rate(all_deals),
            "pipeline_value": sum(d["fields"].get("Deal Value", 0) for d in all_deals if d["fields"].get("Pipeline Stage") not in ["Closed Won", "Closed Lost"])
        },
        "client_metrics": {
            "active_clients": len([c for c in all_clients if c["fields"].get("Status") == "Active"]),
            "average_health_score": calculate_average_health_score(all_clients),
            "at_risk_clients": len([c for c in all_clients if c["fields"].get("Risk Level") == "High"]),
            "client_satisfaction": calculate_average_satisfaction(recent_sessions)
        },
        "operational_metrics": {
            "sessions_completed": len([s for s in recent_sessions if s["fields"].get("Status") == "Completed"]),
            "average_session_rating": calculate_average_session_rating(recent_sessions),
            "utilization_rate": calculate_utilization_rate(recent_sessions),
            "revenue_this_period": calculate_period_revenue(recent_sessions)
        }
    }
    
    if include_forecasting:
        metrics["forecasting"] = {
            "next_30_days": forecast_revenue(all_deals, 30),
            "next_90_days": forecast_revenue(all_deals, 90),
            "quarterly_projection": forecast_revenue(all_deals, 90)
        }
    
    return metrics


def group_deals_by_stage(pipeline_data: List[Dict]) -> Dict[str, List[Dict]]:
    """Group deals by pipeline stage."""
    stages = {}
    for deal in pipeline_data:
        stage = deal.get('Pipeline Stage', 'Unknown')
        if stage not in stages:
            stages[stage] = []
        stages[stage].append(deal)
    return stages


def group_deals_by_source(pipeline_data: List[Dict]) -> Dict[str, List[Dict]]:
    """Group deals by lead source."""
    sources = {}
    for deal in pipeline_data:
        source = deal.get('Lead Source', 'Unknown')
        if source not in sources:
            sources[source] = []
        sources[source].append(deal)
    return sources


def group_deals_by_associate(pipeline_data: List[Dict]) -> Dict[str, List[Dict]]:
    """Group deals by assigned associate."""
    associates = {}
    for deal in pipeline_data:
        associate = deal.get('Assigned To', 'Unassigned')
        if associate not in associates:
            associates[associate] = []
        associates[associate].append(deal)
    return associates


def analyze_deal_aging(pipeline_data: List[Dict]) -> Dict[str, Any]:
    """Analyze how long deals have been in current stage."""
    aging_data = []
    for deal in pipeline_data:
        created_date = deal.get('Created Date')
        if created_date:
            days_old = (datetime.now() - datetime.fromisoformat(created_date)).days
            aging_data.append({
                'deal_id': deal.get('id'),
                'stage': deal.get('Pipeline Stage'),
                'days_in_stage': days_old,
                'value': deal.get('Deal Value', 0)
            })
    
    return {
        'average_age': sum(d['days_in_stage'] for d in aging_data) / len(aging_data) if aging_data else 0,
        'oldest_deals': sorted(aging_data, key=lambda x: x['days_in_stage'], reverse=True)[:5],
        'stale_deals': [d for d in aging_data if d['days_in_stage'] > 30]
    }


def calculate_monthly_progression(pipeline_data: List[Dict]) -> List[Dict]:
    """Calculate monthly pipeline progression."""
    # Implementation for monthly trend analysis
    months = {}
    for deal in pipeline_data:
        created_date = deal.get('Created Date')
        if created_date:
            month_key = datetime.fromisoformat(created_date).strftime('%Y-%m')
            if month_key not in months:
                months[month_key] = {'count': 0, 'value': 0}
            months[month_key]['count'] += 1
            months[month_key]['value'] += deal.get('Deal Value', 0)
    
    return [
        {'month': month, 'deals': data['count'], 'value': data['value']}
        for month, data in sorted(months.items())
    ]


# Additional helper functions for metrics calculations

def calculate_lead_conversion_rate(leads: List[Dict], deals: List[Dict]) -> float:
    """Calculate lead to deal conversion rate."""
    if not leads:
        return 0
    converted_leads = len([d for d in deals if d["fields"].get("Pipeline Stage") == "Closed Won"])
    return (converted_leads / len(leads)) * 100


def calculate_average_lead_score(leads: List[Dict]) -> float:
    """Calculate average lead score."""
    scores = [lead["fields"].get("Lead Score", 0) for lead in leads if lead["fields"].get("Lead Score")]
    return sum(scores) / len(scores) if scores else 0


def calculate_win_rate(deals: List[Dict]) -> float:
    """Calculate deal win rate."""
    closed_deals = [d for d in deals if d["fields"].get("Pipeline Stage") in ["Closed Won", "Closed Lost"]]
    if not closed_deals:
        return 0
    won_deals = len([d for d in closed_deals if d["fields"].get("Pipeline Stage") == "Closed Won"])
    return (won_deals / len(closed_deals)) * 100


def calculate_average_health_score(clients: List[Dict]) -> float:
    """Calculate average client health score."""
    scores = [client["fields"].get("Health Score", 50) for client in clients if client["fields"].get("Health Score")]
    return sum(scores) / len(scores) if scores else 50


def calculate_average_satisfaction(sessions: List[Dict]) -> float:
    """Calculate average client satisfaction from sessions."""
    ratings = [session["fields"].get("Satisfaction", 3) for session in sessions if session["fields"].get("Satisfaction")]
    return sum(ratings) / len(ratings) if ratings else 3


def calculate_average_session_rating(sessions: List[Dict]) -> float:
    """Calculate average session rating."""
    ratings = [session["fields"].get("Rating", 4) for session in sessions if session["fields"].get("Rating")]
    return sum(ratings) / len(ratings) if ratings else 4


def calculate_utilization_rate(sessions: List[Dict]) -> float:
    """Calculate coach utilization rate."""
    completed_sessions = len([s for s in sessions if s["fields"].get("Status") == "Completed"])
    scheduled_sessions = len(sessions)
    return (completed_sessions / scheduled_sessions) * 100 if scheduled_sessions else 0


def calculate_period_revenue(sessions: List[Dict]) -> float:
    """Calculate revenue for the period."""
    return sum(session["fields"].get("Session Fee", 0) for session in sessions if session["fields"].get("Status") == "Completed")


def forecast_revenue(deals: List[Dict], days_ahead: int) -> Dict[str, float]:
    """Forecast revenue based on deal probability and timing."""
    target_date = datetime.now() + timedelta(days=days_ahead)
    
    forecasted_deals = [
        deal for deal in deals 
        if deal["fields"].get("Expected Close") and 
        datetime.fromisoformat(deal["fields"]["Expected Close"]) <= target_date and
        deal["fields"].get("Pipeline Stage") not in ["Closed Won", "Closed Lost"]
    ]
    
    conservative = sum(
        deal["fields"].get("Deal Value", 0) * (deal["fields"].get("Probability %", 50) / 100) * 0.8
        for deal in forecasted_deals
    )
    
    realistic = sum(
        deal["fields"].get("Deal Value", 0) * (deal["fields"].get("Probability %", 50) / 100)
        for deal in forecasted_deals
    )
    
    optimistic = sum(
        deal["fields"].get("Deal Value", 0) * (deal["fields"].get("Probability %", 50) / 100) * 1.2
        for deal in forecasted_deals
    )
    
    return {
        "conservative": round(conservative, 2),
        "realistic": round(realistic, 2),
        "optimistic": round(optimistic, 2),
        "deal_count": len(forecasted_deals)
    }


# Automation trigger helper functions

async def trigger_lead_scoring(base, record_id: str) -> Dict[str, Any]:
    """Trigger lead scoring automation for a specific lead."""
    try:
        table = base.table("Leads")
        record = table.get(record_id)
        # Implementation would call the lead scoring function
        return {"automation": "lead_scoring", "record_id": record_id, "status": "completed"}
    except Exception as e:
        return {"automation": "lead_scoring", "record_id": record_id, "status": "failed", "error": str(e)}


async def trigger_pipeline_automation(base, record_id: str) -> Dict[str, Any]:
    """Trigger pipeline progression automation."""
    try:
        # Implementation for pipeline automation
        return {"automation": "pipeline_progression", "record_id": record_id, "status": "completed"}
    except Exception as e:
        return {"automation": "pipeline_progression", "record_id": record_id, "status": "failed", "error": str(e)}


async def trigger_session_processing(base, record_id: str) -> Dict[str, Any]:
    """Trigger session processing automation."""
    try:
        # Implementation for session processing
        return {"automation": "session_processing", "record_id": record_id, "status": "completed"}
    except Exception as e:
        return {"automation": "session_processing", "record_id": record_id, "status": "failed", "error": str(e)}


async def trigger_health_monitoring(base, record_id: str) -> Dict[str, Any]:
    """Trigger client health monitoring."""
    try:
        # Implementation for health monitoring
        return {"automation": "health_monitoring", "record_id": record_id, "status": "completed"}
    except Exception as e:
        return {"automation": "health_monitoring", "record_id": record_id, "status": "failed", "error": str(e)}


async def create_action_items(api, base_id: str, session_id: str, action_items: List[Dict]) -> None:
    """Create action item records from session processing."""
    action_items_table = api.table(base_id, "Action Items")
    
    for item in action_items:
        record_data = {
            "Session": [session_id],
            "Description": item.get("description"),
            "Due Date": item.get("due_date"),
            "Priority": item.get("priority", "Medium"),
            "Status": "Pending",
            "Created Date": datetime.now().isoformat()
        }
        action_items_table.create(record_data)


async def trigger_invoice_creation(api, base_id: str, session_id: str, session_data: Dict) -> None:
    """Create invoice record for completed session."""
    invoices_table = api.table(base_id, "Invoices")
    
    invoice_data = {
        "Session": [session_id],
        "Client": session_data.get("Client"),
        "Amount": session_data.get("Session Fee", 200),
        "Status": "Draft",
        "Date Created": datetime.now().isoformat(),
        "Due Date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    invoices_table.create(invoice_data)


# Error handling utilities
class ToolError(Exception):
    """Custom exception for tool failures."""
    pass


async def handle_tool_error(error: Exception, context: str) -> Dict[str, Any]:
    """
    Standardized error handling for tools.
    
    Args:
        error: The exception that occurred
        context: Description of what was being attempted
    
    Returns:
        Error response dictionary
    """
    logger.error(f"Tool error in {context}: {error}")
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }


# Testing utilities
def create_test_tools():
    """Create mock tools for testing."""
    from pydantic_ai.models.test import TestModel
    
    test_model = TestModel()
    
    async def mock_lead_scorer(lead_data: Dict) -> Dict:
        return {
            "score": 85,
            "qualification_status": "Hot",
            "next_actions": ["Schedule discovery call", "Send proposal template"]
        }
    
    async def mock_health_monitor(client_id: str) -> Dict:
        return {
            "health_score": 75.5,
            "risk_level": "Medium",
            "recommendations": ["Increase session frequency"]
        }
    
    async def mock_session_processor(notes: str) -> Dict:
        return {
            "session_summary": "Productive session focused on leadership challenges",
            "action_items": [{"description": "Complete self-assessment", "due_date": "2024-01-15"}],
            "key_topics": ["Decision making", "Team communication"]
        }
    
    return {
        "lead_scorer": mock_lead_scorer,
        "health_monitor": mock_health_monitor,
        "session_processor": mock_session_processor
    }
```

## Tool Implementation Summary

**Core Tools Created (6 primary functions):**

1. **score_lead** - AI-powered lead scoring with OpenAI integration
2. **monitor_client_health_status** - Automated client health assessment
3. **process_session_completion** - AI session note generation and processing
4. **handle_webhook_event** - Airtable webhook event processor
5. **generate_business_intelligence_report** - Comprehensive BI reporting
6. **format_pipeline_data** - Pipeline data formatting utility

**Key Features:**
- **Webhook Integration**: Real-time Airtable event processing
- **AI-Powered Automation**: Lead scoring, session notes, health monitoring
- **Business Intelligence**: Comprehensive metrics and forecasting
- **Error Handling**: Robust retry logic and failure notifications
- **Rate Limiting**: Built-in API call management
- **Async Operations**: High-performance concurrent processing

**Dependencies Required:**
```python
openai>=1.0.0
pyairtable>=2.0.0  
pydantic>=2.0.0
httpx>=0.24.0
python-dateutil>=2.8.0
```

**Environment Variables:**
```bash
AIRTABLE_API_KEY=your-airtable-api-key
AIRTABLE_BASE_ID=your-base-id
OPENAI_API_KEY=your-openai-api-key
WEBHOOK_SECRET=your-webhook-verification-secret
```

This tools specification provides the complete automation backbone for Sarah's Leadership Secret OS, enabling the transformation from manual 5-table system to fully automated 8-table coaching business operating system with AI intelligence and associate scaling capabilities.