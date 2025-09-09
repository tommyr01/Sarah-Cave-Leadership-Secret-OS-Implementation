"""
Sarah Cave Leadership OS - Automation Package
Python automation modules for coaching business operations.
"""

from .lead_scoring import score_lead_intelligence
from .session_processing import generate_session_notes
from .client_health import monitor_client_health
from .webhook_processor import process_airtable_webhook
from .business_intelligence import generate_bi_report

__version__ = "1.0.0"
__all__ = [
    "score_lead_intelligence",
    "generate_session_notes", 
    "monitor_client_health",
    "process_airtable_webhook",
    "generate_bi_report"
]