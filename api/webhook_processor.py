"""
Vercel API endpoint for main webhook processing.
Routes Airtable webhooks to appropriate automation services.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
from typing import Dict, Any, Optional

# Add the automation module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation'))

from webhook_processor import WebhookProcessor

app = FastAPI()

# Initialize webhook processor
webhook_processor = None

def get_webhook_processor():
    """Get or create webhook processor instance."""
    global webhook_processor
    if webhook_processor is None:
        config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'airtable_api_key': os.getenv('AIRTABLE_API_KEY'),
            'airtable_base_id': os.getenv('AIRTABLE_BASE_ID')
        }
        webhook_processor = WebhookProcessor(config)
    return webhook_processor

@app.post("/api/webhook")
async def handle_airtable_webhook(request: Request):
    """
    Main webhook endpoint that routes Airtable webhooks to appropriate processors.
    
    This is the single endpoint that Airtable webhooks should call.
    It determines the table and action, then routes to the appropriate automation.
    """
    try:
        # Parse webhook payload
        payload = await request.json()
        
        # Get request headers
        headers = dict(request.headers)
        
        # Get webhook processor
        processor = get_webhook_processor()
        
        # Process the webhook
        result = await processor.process_airtable_webhook(payload, headers, processor.config)
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

@app.post("/api/webhook/leads")
async def handle_leads_webhook(request: Request):
    """Direct webhook endpoint for leads table changes."""
    try:
        payload = await request.json()
        headers = dict(request.headers)
        processor = get_webhook_processor()
        
        # Force processing as leads webhook
        payload['_force_table'] = 'Leads'
        result = await processor.process_airtable_webhook(payload, headers, processor.config)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leads webhook error: {str(e)}")

@app.post("/api/webhook/sessions")
async def handle_sessions_webhook(request: Request):
    """Direct webhook endpoint for coaching sessions table changes."""
    try:
        payload = await request.json()
        headers = dict(request.headers)
        processor = get_webhook_processor()
        
        # Force processing as sessions webhook
        payload['_force_table'] = 'Coaching Sessions'
        result = await processor.process_airtable_webhook(payload, headers, processor.config)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sessions webhook error: {str(e)}")

@app.post("/api/webhook/clients")
async def handle_clients_webhook(request: Request):
    """Direct webhook endpoint for clients table changes."""
    try:
        payload = await request.json()
        headers = dict(request.headers)
        processor = get_webhook_processor()
        
        # Force processing as clients webhook
        payload['_force_table'] = 'Clients'
        result = await processor.process_airtable_webhook(payload, headers, processor.config)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clients webhook error: {str(e)}")

@app.get("/api/webhook/health")
async def health_check():
    """Health check endpoint for webhook processor."""
    try:
        processor = get_webhook_processor()
        return {
            "status": "healthy",
            "service": "webhook_processor",
            "config_loaded": bool(processor.config.get('openai_api_key'))
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/api/health")
async def general_health_check():
    """General health check for all services."""
    services_status = {}
    
    try:
        # Check main webhook processor
        processor = get_webhook_processor()
        services_status['webhook_processor'] = "healthy"
        
        # Check required environment variables
        env_vars = ['OPENAI_API_KEY', 'AIRTABLE_API_KEY', 'AIRTABLE_BASE_ID']
        missing_vars = [var for var in env_vars if not os.getenv(var)]
        
        if missing_vars:
            services_status['environment'] = f"missing variables: {', '.join(missing_vars)}"
        else:
            services_status['environment'] = "healthy"
            
        return JSONResponse(content={
            "status": "healthy",
            "services": services_status,
            "deployment": "vercel_serverless"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "services": services_status,
                "error": str(e)
            }
        )

# For Vercel deployment
def handler(request):
    """Vercel serverless function handler."""
    return app(request)