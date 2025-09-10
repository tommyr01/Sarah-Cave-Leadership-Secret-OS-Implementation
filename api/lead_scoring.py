"""
Vercel API endpoint for lead scoring automation.
Handles Airtable webhooks for new leads and scores them using AI.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
from typing import Dict, Any

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

from lead_scoring import score_lead_intelligence

app = FastAPI()

@app.post("/api/lead_scoring")
async def handle_lead_scoring_webhook(request: Request):
    """
    Vercel serverless function to handle lead scoring webhooks from Airtable.
    
    Expected webhook payload from Airtable:
    {
        "base": {"id": "appXXXXXXXXXXXX"},
        "table": {"id": "tblXXXXXXXXXXXX", "name": "Leads"},
        "webhook": {"id": "achXXXXXXXXXXXX"},
        "timestamp": "2023-01-01T00:00:00.000Z",
        "changedTablesById": {
            "tblXXXXXXXXXXXX": {
                "changedRecordsById": {
                    "recXXXXXXXXXXXX": {
                        "current": {
                            "id": "recXXXXXXXXXXXX",
                            "createdTime": "2023-01-01T00:00:00.000Z",
                            "fields": {
                                "Name": "John Smith",
                                "Email": "john@example.com",
                                "Company": "TechCorp",
                                "Title": "VP Engineering",
                                "Lead Source": "LinkedIn",
                                "Industry": "Technology",
                                "Company Size": "250",
                                "Notes": "Interested in leadership development"
                            }
                        },
                        "previous": null
                    }
                }
            }
        }
    }
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
                previous_record = record_change.get('previous')
                
                # Only process new leads (previous is null) or leads without scores
                if current_record and (
                    previous_record is None or 
                    current_record.get('fields', {}).get('Lead Score') is None
                ):
                    # Extract lead data from Airtable fields
                    fields = current_record.get('fields', {})
                    
                    lead_data = {
                        'name': fields.get('Name', ''),
                        'email': fields.get('Email', ''),
                        'phone': fields.get('Phone', ''),
                        'company': fields.get('Company', ''),
                        'title': fields.get('Title', ''),
                        'lead_source': fields.get('Lead Source', ''),
                        'industry': fields.get('Industry', ''),
                        'company_size': fields.get('Company Size', ''),
                        'notes': fields.get('Notes', '')
                    }
                    
                    # Score the lead using AI
                    scoring_result = await score_lead_intelligence(lead_data, openai_api_key)
                    
                    # TODO: Update Airtable with scoring results
                    # This would require Airtable API integration to write back the results
                    
                    results.append({
                        'record_id': record_id,
                        'lead_name': lead_data['name'],
                        'scoring_result': scoring_result
                    })
        
        return JSONResponse(content={
            "status": "success",
            "processed_leads": len(results),
            "results": results
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/lead_scoring/health")
async def health_check():
    """Health check endpoint for lead scoring service."""
    return {"status": "healthy", "service": "lead_scoring"}

# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request)