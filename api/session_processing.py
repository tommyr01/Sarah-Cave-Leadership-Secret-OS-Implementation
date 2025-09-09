"""
Vercel API endpoint for session processing automation.
Handles Airtable webhooks for coaching session updates and processes notes using AI.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
from typing import Dict, Any

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

from session_processing import process_session_intelligence

app = FastAPI()

@app.post("/api/session_processing")
async def handle_session_processing_webhook(request: Request):
    """
    Vercel serverless function to handle session processing webhooks from Airtable.
    
    Processes coaching session notes and generates AI-powered summaries and action items.
    """
    try:
        # Get API keys from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Parse webhook payload
        payload = await request.json()
        
        # Validate webhook structure
        if 'changedTablesById' not in payload:
            return JSONResponse(content={"status": "ignored", "reason": "No changed tables"})
        
        results = []
        
        # Process each changed table
        for table_id, table_changes in payload['changedTablesById'].items():
            if 'changedRecordsById' not in table_changes:
                continue
                
            # Process each changed record
            for record_id, record_change in table_changes['changedRecordsById'].items():
                current_record = record_change.get('current')
                
                # Only process sessions with raw notes that need processing
                if current_record:
                    fields = current_record.get('fields', {})
                    
                    # Check if session has raw notes but no processed summary
                    raw_notes = fields.get('Raw Notes', '')
                    processed_summary = fields.get('Session Summary', '')
                    
                    if raw_notes and not processed_summary:
                        # Extract session data
                        session_data = {
                            'client_name': fields.get('Client Name', ''),
                            'session_date': fields.get('Session Date', ''),
                            'session_type': fields.get('Session Type', 'Leadership Coaching'),
                            'duration': fields.get('Duration (minutes)', 60),
                            'raw_notes': raw_notes,
                            'session_objectives': fields.get('Session Objectives', ''),
                            'client_context': fields.get('Client Context', ''),
                            'previous_action_items': fields.get('Previous Action Items', ''),
                            'coaching_focus_areas': fields.get('Coaching Focus Areas', [])
                        }
                        
                        # Process session using AI
                        processing_result = await process_session_intelligence(session_data, openai_api_key)
                        
                        # TODO: Update Airtable with processing results
                        # This would require Airtable API integration to write back:
                        # - Session Summary
                        # - Key Insights
                        # - Action Items
                        # - Follow-up Tasks
                        # - Client Progress Notes
                        
                        results.append({
                            'record_id': record_id,
                            'client_name': session_data['client_name'],
                            'processing_result': processing_result
                        })
        
        return JSONResponse(content={
            "status": "success",
            "processed_sessions": len(results),
            "results": results
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/session_processing/health")
async def health_check():
    """Health check endpoint for session processing service."""
    return {"status": "healthy", "service": "session_processing"}

# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request)