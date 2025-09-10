"""
Main webhook processor and router for Sarah Cave's Leadership Secret Operating System.
Handles all incoming Airtable webhooks and routes them to appropriate automation functions.
"""

from typing import Dict, Any, List, Optional, Callable
import json
import hashlib
import hmac
import traceback
from datetime import datetime
from enum import Enum
import asyncio

# Import automation modules
from .lead_scoring import score_lead_intelligence
from .session_processing import process_session_intelligence
from .client_health import assess_client_health_intelligence

class WebhookType(str, Enum):
    LEAD_CREATED = "lead_created"
    LEAD_UPDATED = "lead_updated"
    SESSION_CREATED = "session_created"
    SESSION_UPDATED = "session_updated"
    CLIENT_UPDATED = "client_updated"
    PAYMENT_UPDATED = "payment_updated"
    ACTION_ITEM_UPDATED = "action_item_updated"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    SKIPPED = "skipped"

class WebhookProcessor:
    """
    Main webhook processing engine for Sarah Cave's coaching automation system.
    Routes Airtable webhook payloads to appropriate automation functions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook processor with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - airtable_webhook_secret: Secret for webhook authentication
                - openai_api_key: OpenAI API key for AI processing
                - base_id: Airtable base ID
                - table_mappings: Mapping of table names to processing functions
                - enabled_automations: List of enabled automation types
                - rate_limit_settings: Rate limiting configuration
        """
        self.config = config
        self.webhook_secret = config.get('airtable_webhook_secret', '')
        self.openai_api_key = config.get('openai_api_key', '')
        self.base_id = config.get('base_id', '')
        self.enabled_automations = config.get('enabled_automations', [])
        
        # Initialize processing handlers
        self.handlers = self._initialize_handlers()
        
        # Rate limiting and error tracking
        self.processing_history = []
        self.error_count = {}
        
    def _initialize_handlers(self) -> Dict[WebhookType, Callable]:
        """Initialize mapping of webhook types to processing functions."""
        return {
            WebhookType.LEAD_CREATED: self._process_lead_scoring,
            WebhookType.LEAD_UPDATED: self._process_lead_scoring,
            WebhookType.SESSION_CREATED: self._process_session_notes,
            WebhookType.SESSION_UPDATED: self._process_session_notes,
            WebhookType.CLIENT_UPDATED: self._process_client_health,
            WebhookType.PAYMENT_UPDATED: self._process_client_health,
            WebhookType.ACTION_ITEM_UPDATED: self._process_action_item_update,
        }
    
    async def process_webhook(self, payload: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Main webhook processing entry point.
        
        Args:
            payload: Airtable webhook payload
            headers: HTTP headers from webhook request
        
        Returns:
            Processing result dictionary with status and details
        """
        
        processing_start = datetime.utcnow()
        
        try:
            # Authenticate webhook
            if not self._authenticate_webhook(payload, headers):
                return self._create_error_response("Authentication failed", "AUTHENTICATION_ERROR")
            
            # Parse webhook payload
            webhook_info = self._parse_webhook_payload(payload)
            
            # Check if automation is enabled
            if not self._is_automation_enabled(webhook_info['webhook_type']):
                return self._create_response(ProcessingStatus.SKIPPED, f"Automation for {webhook_info['webhook_type']} is disabled")
            
            # Route to appropriate handler
            handler = self.handlers.get(webhook_info['webhook_type'])
            if not handler:
                return self._create_response(ProcessingStatus.SKIPPED, f"No handler for webhook type: {webhook_info['webhook_type']}")
            
            # Process webhook with appropriate handler
            processing_result = await handler(webhook_info, payload)
            
            # Log processing result
            self._log_processing_result(webhook_info, processing_result, processing_start)
            
            return processing_result
            
        except Exception as e:
            error_message = f"Webhook processing failed: {str(e)}"
            error_details = traceback.format_exc()
            
            self._log_error(webhook_info if 'webhook_info' in locals() else {}, error_message, error_details)
            
            return self._create_error_response(error_message, "PROCESSING_ERROR", error_details)
    
    def _authenticate_webhook(self, payload: Dict[str, Any], headers: Dict[str, str] = None) -> bool:
        """
        Authenticate webhook request using Airtable webhook signature.
        
        Args:
            payload: Webhook payload
            headers: HTTP headers containing signature
        
        Returns:
            True if authentication successful, False otherwise
        """
        
        if not self.webhook_secret:
            # If no secret configured, skip authentication (development mode)
            return True
        
        if not headers:
            return False
        
        # Get signature from headers
        signature = headers.get('x-airtable-webhook-signature') or headers.get('X-Airtable-Webhook-Signature')
        if not signature:
            return False
        
        # Calculate expected signature
        payload_string = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    def _parse_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Airtable webhook payload to extract relevant information.
        
        Args:
            payload: Raw webhook payload from Airtable
        
        Returns:
            Parsed webhook information
        """
        
        # Extract basic webhook info
        webhook_spec = payload.get('webhook', {})
        base_id = payload.get('base', {}).get('id', '')
        
        # Extract changed records
        changed_tables = payload.get('changedTablesById', {})
        
        # Determine webhook type based on changed tables and records
        webhook_type = self._determine_webhook_type(changed_tables)
        
        # Extract record changes
        record_changes = self._extract_record_changes(changed_tables)
        
        return {
            'webhook_id': webhook_spec.get('id', ''),
            'webhook_type': webhook_type,
            'base_id': base_id,
            'timestamp': payload.get('timestamp', datetime.utcnow().isoformat()),
            'changed_tables': list(changed_tables.keys()),
            'record_changes': record_changes,
            'total_records_changed': sum(len(table.get('changedRecordsById', {})) for table in changed_tables.values())
        }
    
    def _determine_webhook_type(self, changed_tables: Dict[str, Any]) -> WebhookType:
        """
        Determine webhook type based on which tables changed.
        
        Args:
            changed_tables: Dictionary of changed tables from webhook payload
        
        Returns:
            WebhookType enum indicating the type of webhook
        """
        
        # Table name to webhook type mapping
        table_mappings = {
            'Leads': WebhookType.LEAD_UPDATED,
            'Lead': WebhookType.LEAD_UPDATED,
            'Sessions': WebhookType.SESSION_UPDATED,
            'Coaching Sessions': WebhookType.SESSION_UPDATED,
            'Clients': WebhookType.CLIENT_UPDATED,
            'Client': WebhookType.CLIENT_UPDATED,
            'Invoices': WebhookType.PAYMENT_UPDATED,
            'Action Items': WebhookType.ACTION_ITEM_UPDATED,
            'Action Item': WebhookType.ACTION_ITEM_UPDATED
        }
        
        # Check each changed table
        for table_id, table_data in changed_tables.items():
            table_name = table_data.get('name', '')
            
            # Check for exact table name matches
            for mapped_table, webhook_type in table_mappings.items():
                if mapped_table.lower() in table_name.lower():
                    
                    # Check if this is a creation (new record) vs update
                    created_records = table_data.get('createdRecordsById', {})
                    if created_records and webhook_type in [WebhookType.LEAD_UPDATED, WebhookType.SESSION_UPDATED]:
                        # Convert to creation type if records were created
                        if webhook_type == WebhookType.LEAD_UPDATED:
                            return WebhookType.LEAD_CREATED
                        elif webhook_type == WebhookType.SESSION_UPDATED:
                            return WebhookType.SESSION_CREATED
                    
                    return webhook_type
        
        return WebhookType.UNKNOWN
    
    def _extract_record_changes(self, changed_tables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract detailed record changes from webhook payload.
        
        Args:
            changed_tables: Changed tables data from webhook
        
        Returns:
            List of record change details
        """
        
        record_changes = []
        
        for table_id, table_data in changed_tables.items():
            table_name = table_data.get('name', 'Unknown Table')
            
            # Process created records
            created_records = table_data.get('createdRecordsById', {})
            for record_id, record_data in created_records.items():
                record_changes.append({
                    'table_id': table_id,
                    'table_name': table_name,
                    'record_id': record_id,
                    'change_type': 'created',
                    'fields': record_data.get('fields', {}),
                    'created_time': record_data.get('createdTime')
                })
            
            # Process changed records
            changed_records = table_data.get('changedRecordsById', {})
            for record_id, change_data in changed_records.items():
                # Extract previous and current field values
                previous_fields = change_data.get('previous', {}).get('fields', {})
                current_fields = change_data.get('current', {}).get('fields', {})
                
                record_changes.append({
                    'table_id': table_id,
                    'table_name': table_name,
                    'record_id': record_id,
                    'change_type': 'updated',
                    'previous_fields': previous_fields,
                    'current_fields': current_fields,
                    'changed_fields': list(set(previous_fields.keys()) | set(current_fields.keys()))
                })
            
            # Process destroyed records
            destroyed_records = table_data.get('destroyedRecordIds', [])
            for record_id in destroyed_records:
                record_changes.append({
                    'table_id': table_id,
                    'table_name': table_name,
                    'record_id': record_id,
                    'change_type': 'destroyed'
                })
        
        return record_changes
    
    def _is_automation_enabled(self, webhook_type: WebhookType) -> bool:
        """Check if automation is enabled for this webhook type."""
        
        if not self.enabled_automations:
            return True  # If no specific automations listed, enable all
        
        automation_mappings = {
            WebhookType.LEAD_CREATED: 'lead_scoring',
            WebhookType.LEAD_UPDATED: 'lead_scoring',
            WebhookType.SESSION_CREATED: 'session_processing',
            WebhookType.SESSION_UPDATED: 'session_processing',
            WebhookType.CLIENT_UPDATED: 'client_health',
            WebhookType.PAYMENT_UPDATED: 'client_health',
            WebhookType.ACTION_ITEM_UPDATED: 'action_item_tracking'
        }
        
        automation_type = automation_mappings.get(webhook_type)
        return automation_type in self.enabled_automations if automation_type else False
    
    async def _process_lead_scoring(self, webhook_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process lead scoring automation."""
        
        results = []
        errors = []
        
        try:
            for record_change in webhook_info['record_changes']:
                if 'lead' not in record_change['table_name'].lower():
                    continue
                
                # Extract lead data for scoring
                if record_change['change_type'] == 'created':
                    lead_data = record_change['fields']
                elif record_change['change_type'] == 'updated':
                    lead_data = record_change['current_fields']
                else:
                    continue
                
                # Prepare lead data for scoring
                scoring_data = self._prepare_lead_data(lead_data, record_change['record_id'])
                
                # Process lead scoring
                scoring_result = await score_lead_intelligence(scoring_data, self.openai_api_key)
                
                # Store result with record info
                results.append({
                    'record_id': record_change['record_id'],
                    'table_name': record_change['table_name'],
                    'automation_type': 'lead_scoring',
                    'result': scoring_result,
                    'processed_at': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            errors.append(f"Lead scoring failed: {str(e)}")
        
        return self._create_processing_response(results, errors, 'lead_scoring')
    
    async def _process_session_notes(self, webhook_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process session note generation automation."""
        
        results = []
        errors = []
        
        try:
            for record_change in webhook_info['record_changes']:
                if 'session' not in record_change['table_name'].lower():
                    continue
                
                # Extract session data for processing
                if record_change['change_type'] == 'created':
                    session_data = record_change['fields']
                elif record_change['change_type'] == 'updated':
                    session_data = record_change['current_fields']
                else:
                    continue
                
                # Check if raw notes are present (trigger for processing)
                if not session_data.get('raw_notes') and not session_data.get('Raw Notes'):
                    continue  # Skip if no notes to process
                
                # Prepare session data for processing
                processing_data = self._prepare_session_data(session_data, record_change['record_id'])
                
                # Process session notes
                processing_result = await process_session_intelligence(processing_data, self.openai_api_key)
                
                # Store result
                results.append({
                    'record_id': record_change['record_id'],
                    'table_name': record_change['table_name'],
                    'automation_type': 'session_processing',
                    'result': processing_result,
                    'processed_at': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            errors.append(f"Session processing failed: {str(e)}")
        
        return self._create_processing_response(results, errors, 'session_processing')
    
    async def _process_client_health(self, webhook_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process client health monitoring automation."""
        
        results = []
        errors = []
        
        try:
            # Get unique client IDs from changes
            client_ids = set()
            
            for record_change in webhook_info['record_changes']:
                table_name = record_change['table_name'].lower()
                
                if 'client' in table_name:
                    client_ids.add(record_change['record_id'])
                elif 'payment' in table_name or 'invoice' in table_name:
                    # Get client ID from payment/invoice record
                    fields = record_change.get('current_fields', record_change.get('fields', {}))
                    client_link = fields.get('Client', fields.get('client', []))
                    if isinstance(client_link, list) and client_link:
                        client_ids.add(client_link[0])
            
            # Process health assessment for each affected client
            for client_id in client_ids:
                # Prepare client health data (would normally fetch from Airtable)
                client_data = self._prepare_client_health_data(client_id, webhook_info)
                
                # Process client health assessment
                health_result = await assess_client_health_intelligence(client_data, self.openai_api_key)
                
                # Store result
                results.append({
                    'client_id': client_id,
                    'automation_type': 'client_health',
                    'result': health_result,
                    'processed_at': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            errors.append(f"Client health assessment failed: {str(e)}")
        
        return self._create_processing_response(results, errors, 'client_health')
    
    async def _process_action_item_update(self, webhook_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process action item updates (may trigger client health reassessment)."""
        
        results = []
        errors = []
        
        try:
            # Track clients who need health reassessment due to action item changes
            clients_to_reassess = set()
            
            for record_change in webhook_info['record_changes']:
                if 'action' not in record_change['table_name'].lower():
                    continue
                
                # Get client ID from action item
                fields = record_change.get('current_fields', record_change.get('fields', {}))
                client_link = fields.get('Client', fields.get('client', []))
                
                if isinstance(client_link, list) and client_link:
                    clients_to_reassess.add(client_link[0])
                
                # Log action item change
                results.append({
                    'record_id': record_change['record_id'],
                    'table_name': record_change['table_name'],
                    'automation_type': 'action_item_tracking',
                    'result': {
                        'action': 'logged_change',
                        'change_type': record_change['change_type'],
                        'status': fields.get('Status', 'unknown')
                    },
                    'processed_at': datetime.utcnow().isoformat()
                })
            
            # Trigger client health reassessment for affected clients
            for client_id in clients_to_reassess:
                try:
                    client_data = self._prepare_client_health_data(client_id, webhook_info)
                    health_result = await assess_client_health_intelligence(client_data, self.openai_api_key)
                    
                    results.append({
                        'client_id': client_id,
                        'automation_type': 'client_health_reassessment',
                        'result': health_result,
                        'processed_at': datetime.utcnow().isoformat(),
                        'triggered_by': 'action_item_update'
                    })
                    
                except Exception as e:
                    errors.append(f"Client health reassessment failed for {client_id}: {str(e)}")
                
        except Exception as e:
            errors.append(f"Action item processing failed: {str(e)}")
        
        return self._create_processing_response(results, errors, 'action_item_processing')
    
    def _prepare_lead_data(self, fields: Dict[str, Any], record_id: str) -> Dict[str, Any]:
        """Prepare lead data for scoring automation."""
        
        # Map Airtable field names to expected format
        return {
            'name': fields.get('Name', fields.get('Lead Name', 'Unknown Lead')),
            'email': fields.get('Email', fields.get('Email Address', '')),
            'phone': fields.get('Phone', fields.get('Phone Number', '')),
            'company': fields.get('Company', fields.get('Company Name', '')),
            'title': fields.get('Title', fields.get('Job Title', '')),
            'lead_source': fields.get('Lead Source', fields.get('Source', 'Unknown')),
            'industry': fields.get('Industry', ''),
            'company_size': fields.get('Company Size', ''),
            'engagement_history': fields.get('Engagement History', []),
            'notes': fields.get('Notes', fields.get('Additional Notes', '')),
            'record_id': record_id
        }
    
    def _prepare_session_data(self, fields: Dict[str, Any], record_id: str) -> Dict[str, Any]:
        """Prepare session data for processing automation."""
        
        return {
            'client_name': fields.get('Client Name', fields.get('Client', 'Unknown Client')),
            'session_date': fields.get('Session Date', fields.get('Date', datetime.utcnow().isoformat())),
            'session_duration': fields.get('Duration', fields.get('Session Duration', 60)),
            'session_type': fields.get('Session Type', '1-on-1 Coaching'),
            'leadership_model': fields.get('Leadership Model', fields.get('Model Used', '')),
            'client_goals': fields.get('Client Goals', ''),
            'raw_notes': fields.get('Raw Notes', fields.get('raw_notes', '')),
            'previous_actions': fields.get('Previous Action Items', ''),
            'record_id': record_id
        }
    
    def _prepare_client_health_data(self, client_id: str, webhook_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare client health data for assessment."""
        
        # This would normally fetch comprehensive client data from Airtable
        # For now, return basic structure with client ID
        return {
            'client_name': f'Client {client_id}',
            'client_id': client_id,
            'last_session_date': datetime.utcnow().isoformat(),
            'session_history': [],
            'payment_history': [],
            'action_items': [],
            'communication_log': [],
            'satisfaction_scores': [],
            'goal_progress': {},
            'notes': f'Health assessment triggered by webhook: {webhook_info.get("webhook_type", "unknown")}'
        }
    
    def _create_processing_response(self, results: List[Dict[str, Any]], errors: List[str], automation_type: str) -> Dict[str, Any]:
        """Create standardized processing response."""
        
        if not results and not errors:
            status = ProcessingStatus.SKIPPED
        elif errors and not results:
            status = ProcessingStatus.FAILED
        elif errors and results:
            status = ProcessingStatus.PARTIAL_SUCCESS
        else:
            status = ProcessingStatus.SUCCESS
        
        return {
            'status': status.value,
            'automation_type': automation_type,
            'results_count': len(results),
            'error_count': len(errors),
            'results': results,
            'errors': errors,
            'processed_at': datetime.utcnow().isoformat(),
            'processing_duration_ms': 0  # Would be calculated from start time
        }
    
    def _create_response(self, status: ProcessingStatus, message: str, details: Any = None) -> Dict[str, Any]:
        """Create standardized response."""
        
        response = {
            'status': status.value,
            'message': message,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        if details:
            response['details'] = details
        
        return response
    
    def _create_error_response(self, error_message: str, error_code: str, error_details: str = None) -> Dict[str, Any]:
        """Create standardized error response."""
        
        response = {
            'status': ProcessingStatus.FAILED.value,
            'error': error_message,
            'error_code': error_code,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        if error_details:
            response['error_details'] = error_details
        
        return response
    
    def _log_processing_result(self, webhook_info: Dict[str, Any], result: Dict[str, Any], start_time: datetime):
        """Log processing result for monitoring and debugging."""
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        log_entry = {
            'webhook_type': webhook_info.get('webhook_type'),
            'webhook_id': webhook_info.get('webhook_id'),
            'records_processed': webhook_info.get('total_records_changed', 0),
            'processing_status': result.get('status'),
            'processing_duration_ms': duration,
            'timestamp': datetime.utcnow().isoformat(),
            'errors': result.get('errors', [])
        }
        
        self.processing_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
    
    def _log_error(self, webhook_info: Dict[str, Any], error_message: str, error_details: str):
        """Log error for monitoring and debugging."""
        
        webhook_type = webhook_info.get('webhook_type', 'unknown')
        
        if webhook_type not in self.error_count:
            self.error_count[webhook_type] = 0
        
        self.error_count[webhook_type] += 1
        
        error_log = {
            'webhook_type': webhook_type,
            'error_message': error_message,
            'error_details': error_details,
            'timestamp': datetime.utcnow().isoformat(),
            'error_count_for_type': self.error_count[webhook_type]
        }
        
        # In production, this would log to external monitoring service
        print(f"WEBHOOK ERROR: {json.dumps(error_log, indent=2)}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring dashboard."""
        
        total_processed = len(self.processing_history)
        successful = sum(1 for entry in self.processing_history if entry['processing_status'] == 'success')
        failed = sum(1 for entry in self.processing_history if entry['processing_status'] == 'failed')
        
        avg_duration = 0
        if self.processing_history:
            avg_duration = sum(entry['processing_duration_ms'] for entry in self.processing_history) / len(self.processing_history)
        
        return {
            'total_webhooks_processed': total_processed,
            'successful_processing': successful,
            'failed_processing': failed,
            'success_rate': (successful / max(total_processed, 1)) * 100,
            'average_processing_duration_ms': round(avg_duration, 2),
            'error_counts_by_type': self.error_count,
            'last_24h_processing': [
                entry for entry in self.processing_history
                if (datetime.utcnow() - datetime.fromisoformat(entry['timestamp'])).days < 1
            ]
        }

# Public interface function for serverless deployment
async def process_airtable_webhook(payload: Dict[str, Any], headers: Dict[str, str], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function for processing Airtable webhooks - called by serverless function.
    
    Args:
        payload: Airtable webhook payload
        headers: HTTP headers from request
        config: Application configuration
    
    Returns:
        Processing result dictionary
    """
    
    processor = WebhookProcessor(config)
    return await processor.process_webhook(payload, headers)

# Health check endpoint
def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    
    return {
        'status': 'healthy',
        'service': 'webhook_processor',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'supported_webhooks': [wt.value for wt in WebhookType if wt != WebhookType.UNKNOWN]
    }

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test configuration
    test_config = {
        'airtable_webhook_secret': 'test-secret',
        'openai_api_key': 'test-api-key',
        'base_id': 'appovmJ15ALIjbpDp',
        'enabled_automations': ['lead_scoring', 'session_processing', 'client_health']
    }
    
    # Test webhook payload
    test_payload = {
        'webhook': {'id': 'webhook-123'},
        'base': {'id': 'appovmJ15ALIjbpDp'},
        'timestamp': '2024-12-09T10:00:00.000Z',
        'changedTablesById': {
            'tbl123': {
                'name': 'Leads',
                'createdRecordsById': {
                    'rec456': {
                        'fields': {
                            'Name': 'John Smith',
                            'Email': 'john@techcorp.com',
                            'Company': 'TechCorp Inc',
                            'Title': 'VP Engineering',
                            'Lead Source': 'LinkedIn'
                        },
                        'createdTime': '2024-12-09T10:00:00.000Z'
                    }
                }
            }
        }
    }
    
    async def test_webhook_processing():
        # Test webhook processing
        result = await process_airtable_webhook(test_payload, {}, test_config)
        print("Webhook Processing Result:")
        print(json.dumps(result, indent=2))
        
        # Test health check
        health = health_check()
        print("\nHealth Check Result:")
        print(json.dumps(health, indent=2))
    
    # asyncio.run(test_webhook_processing())  # Uncomment to test