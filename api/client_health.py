"""
Vercel API endpoint for client health monitoring automation.
Handles periodic assessment of client health and engagement levels.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
from typing import Dict, Any

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

from client_health import assess_client_health_intelligence

app = FastAPI()

@app.post("/api/client_health")
async def handle_client_health_assessment(request: Request):
    """
    Vercel serverless function to handle client health monitoring.
    
    Can be triggered by:
    1. Airtable webhooks when client data changes
    2. Scheduled function for periodic health assessments
    3. Manual triggers for specific client reviews
    """
    try:
        # Get API keys from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Parse request payload
        payload = await request.json()
        
        results = []
        
        # Handle different payload types
        if 'changedTablesById' in payload:
            # Airtable webhook payload - process changed client records
            for table_id, table_changes in payload['changedTablesById'].items():
                if 'changedRecordsById' not in table_changes:
                    continue
                    
                for record_id, record_change in table_changes['changedRecordsById'].items():
                    current_record = record_change.get('current')
                    
                    if current_record:
                        fields = current_record.get('fields', {})
                        client_data = extract_client_data(fields)
                        
                        # Assess client health
                        health_result = await assess_client_health_intelligence(client_data, openai_api_key)
                        
                        results.append({
                            'record_id': record_id,
                            'client_name': client_data['client_name'],
                            'health_result': health_result
                        })
        
        elif 'clients' in payload:
            # Direct client assessment payload
            for client_data in payload['clients']:
                health_result = await assess_client_health_intelligence(client_data, openai_api_key)
                
                results.append({
                    'client_name': client_data['client_name'],
                    'health_result': health_result
                })
        
        else:
            raise HTTPException(status_code=400, detail="Invalid payload format")
        
        return JSONResponse(content={
            "status": "success",
            "assessed_clients": len(results),
            "results": results
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/client_health/bulk_assessment")
async def trigger_bulk_health_assessment():
    """
    Endpoint to trigger bulk client health assessment.
    
    This would typically be called by a scheduled function to assess
    all active clients periodically.
    """
    try:
        # TODO: Fetch all active clients from Airtable
        # TODO: Assess health for each client
        # TODO: Update health scores in Airtable
        
        return JSONResponse(content={
            "status": "success",
            "message": "Bulk health assessment triggered",
            "note": "Implementation requires Airtable API integration"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk assessment error: {str(e)}")

@app.get("/api/client_health/health")
async def health_check():
    """Health check endpoint for client health monitoring service."""
    return {"status": "healthy", "service": "client_health"}

def extract_client_data(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Extract client data from Airtable fields."""
    return {
        'client_name': fields.get('Name', ''),
        'email': fields.get('Email', ''),
        'company': fields.get('Company', ''),
        'title': fields.get('Title', ''),
        'coaching_start_date': fields.get('Coaching Start Date', ''),
        'last_session_date': fields.get('Last Session Date', ''),
        'total_sessions': fields.get('Total Sessions', 0),
        'session_frequency': fields.get('Session Frequency', 'Bi-weekly'),
        'engagement_level': fields.get('Engagement Level', 'Medium'),
        'payment_status': fields.get('Payment Status', 'Current'),
        'satisfaction_score': fields.get('Satisfaction Score', 0),
        'goals_progress': fields.get('Goals Progress', ''),
        'challenges': fields.get('Current Challenges', ''),
        'communication_preference': fields.get('Communication Preference', 'Email'),
        'notes': fields.get('Notes', '')
    }

# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request)