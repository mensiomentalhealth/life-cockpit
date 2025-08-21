"""
Dynamics Message Processor

Processes messages from the actual Dynamics cre92_scheduledmessage table.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from utils.guardrails import safe_operation, Classification, create_run_id
from utils.sandbox import get_sandbox_dataverse
from azure.messaging import MessagingFactory

logger = structlog.get_logger()

class DynamicsMessageProcessor:
    """Processes messages from Dynamics cre92_scheduledmessage table"""
    
    def __init__(self):
        self.dataverse = get_sandbox_dataverse()  # Will use real Dataverse when sandbox disabled
        
        # Initialize messaging factory with providers
        messaging_config = {
            'graph': {
                'tenant_id': os.getenv('GRAPH_TENANT_ID', 'mock-tenant'),
                'client_id': os.getenv('GRAPH_CLIENT_ID', 'mock-client'),
                'client_secret': os.getenv('GRAPH_CLIENT_SECRET', 'mock-secret')
            },
            'respond': {
                'api_key': os.getenv('RESPOND_API_KEY', 'mock-key'),
                'workspace_id': os.getenv('RESPOND_WORKSPACE_ID', 'mock-workspace'),
                'base_url': os.getenv('RESPOND_BASE_URL', 'https://api.respond.io')
            }
        }
        
        self.messaging_factory = MessagingFactory(messaging_config)
        
        logger.info("DynamicsMessageProcessor initialized with messaging factory")
    
    @safe_operation(Classification.BUSINESS, "dynamics-message-process")
    async def process_dynamics_messages(self, run_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Process messages from Dynamics cre92_scheduledmessage table"""
        
        if not run_id:
            run_id = create_run_id("dynamics-message-process", Classification.BUSINESS)
        
        logger.info("Starting Dynamics message processing", run_id=run_id, dry_run=dry_run)
        
        try:
            # Query pending messages from Dynamics table
            messages = await self._query_pending_dynamics_messages()
            
            if not messages:
                logger.info("No pending messages found in Dynamics", run_id=run_id)
                return {
                    'status': 'success',
                    'processed_count': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'run_id': run_id
                }
            
            logger.info(f"Found {len(messages)} pending messages in Dynamics", run_id=run_id)
            
            # Process each message
            results = []
            for message in messages:
                try:
                    result = await self._process_dynamics_message(message, dry_run)
                    results.append(result)
                except Exception as e:
                    logger.error("Failed to process Dynamics message", 
                               message_id=message.get('MessageID'), 
                               error=str(e), 
                               run_id=run_id)
                    result = {
                        'status': 'failed',
                        'message_id': message.get('MessageID'),
                        'error': str(e)
                    }
                    results.append(result)
                    
                    # Mark message as failed in Dynamics
                    if not dry_run:
                        await self._mark_dynamics_message_failed(message.get('MessageID'), str(e))
            
            # Calculate statistics
            success_count = len([r for r in results if r['status'] == 'success'])
            failed_count = len([r for r in results if r['status'] == 'failed'])
            
            logger.info("Dynamics message processing completed", 
                       run_id=run_id,
                       processed_count=len(results),
                       success_count=success_count,
                       failed_count=failed_count)
            
            return {
                'status': 'success',
                'processed_count': len(results),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results,
                'run_id': run_id
            }
            
        except Exception as e:
            logger.error("Dynamics message processing failed", error=str(e), run_id=run_id)
            raise
    
    async def _query_pending_dynamics_messages(self) -> List[Dict[str, Any]]:
        """Query pending messages from Dynamics cre92_scheduledmessage table"""
        try:
            # Query messages that are ready to send
            # MessageStatus = 'Revised' OR MessageStatus = 2
            # AND ScheduledTimestamp <= utcNow()
            # AND Sent = false
            filter_query = "(MessageStatus eq 'Revised' or MessageStatus eq 2) and ScheduledTimestamp le utcNow() and Sent eq false"
            
            messages = await self.dataverse.query_records(
                'cre92_scheduledmessage',
                filter=filter_query,
                orderby='ScheduledTimestamp asc',
                top=50  # Process in batches
            )
            
            logger.info(f"Queried {len(messages)} pending messages from Dynamics")
            return messages
            
        except Exception as e:
            logger.error("Failed to query pending Dynamics messages", error=str(e))
            raise
    
    async def _process_dynamics_message(self, message: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Process a single Dynamics message"""
        message_id = message.get('MessageID')
        message_type = message.get('MessageType', 'email')
        
        logger.info("Processing Dynamics message", 
                   message_id=message_id, 
                   message_type=message_type, 
                   dry_run=dry_run)
        
        if dry_run:
            return {
                'status': 'dry_run',
                'message_id': message_id,
                'message_type': message_type,
                'recipient': message.get('Email'),
                'subject': message.get('MessageSubject')
            }
        
        try:
            # Convert Dynamics message to our messaging format
            messaging_message = self._convert_dynamics_to_messaging_format(message)
            
            # Use messaging factory to send message
            result = await self.messaging_factory.send_message(messaging_message)
            
            if result.success:
                # Log to messages_log
                await self._log_dynamics_message_sent(message, result)
                
                # Update Dynamics message status
                await self._mark_dynamics_message_sent(message_id, result.external_id)
                
                return {
                    'status': 'success',
                    'message_id': message_id,
                    'message_type': message_type,
                    'external_id': result.external_id,
                    'provider': result.provider
                }
            else:
                # Mark message as failed
                await self._mark_dynamics_message_failed(message_id, result.error_message)
                
                return {
                    'status': 'failed',
                    'message_id': message_id,
                    'message_type': message_type,
                    'error': result.error_message
                }
            
        except Exception as e:
            logger.error("Failed to process Dynamics message", 
                        message_id=message_id, 
                        error=str(e))
            raise
    
    def _convert_dynamics_to_messaging_format(self, dynamics_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Dynamics message format to our messaging format"""
        message_type = dynamics_message.get('MessageType', 'email')
        
        # Base message structure
        messaging_message = {
            'message_type': message_type,
            'body': dynamics_message.get('MessageText', ''),
            'id': dynamics_message.get('MessageID')  # For tracking
        }
        
        # Add type-specific fields
        if message_type == 'email':
            messaging_message.update({
                'recipient': dynamics_message.get('Email'),
                'subject': dynamics_message.get('MessageSubject')
            })
        elif message_type == 'telegram':
            messaging_message.update({
                'chat_id': dynamics_message.get('TelegramID')
            })
        elif message_type == 'whatsapp':
            messaging_message.update({
                'recipient': dynamics_message.get('WhatsAppID')
            })
        elif message_type == 'sms':
            messaging_message.update({
                'recipient': dynamics_message.get('PhoneNumber')
            })
        
        return messaging_message
    
    async def _log_dynamics_message_sent(self, dynamics_message: Dict[str, Any], result) -> None:
        """Log sent Dynamics message to messages_log table"""
        try:
            log_entry = {
                'message_id': dynamics_message.get('MessageID'),
                'message_type': dynamics_message.get('MessageType', 'email'),
                'recipient': dynamics_message.get('Email') or dynamics_message.get('TelegramID') or dynamics_message.get('WhatsAppID') or dynamics_message.get('PhoneNumber'),
                'subject': dynamics_message.get('MessageSubject'),
                'body': dynamics_message.get('MessageText'),
                'status': 'sent',
                'sent_at': datetime.utcnow().isoformat(),
                'provider': result.provider,
                'message_id_external': result.external_id
            }
            
            await self.dataverse.create_record('messages_log', log_entry)
            
            logger.info("Logged Dynamics message sent", 
                       message_id=dynamics_message.get('MessageID'), 
                       external_id=result.external_id)
            
        except Exception as e:
            logger.error("Failed to log Dynamics message sent", 
                        message_id=dynamics_message.get('MessageID'), 
                        error=str(e))
            # Don't raise - logging failure shouldn't fail the whole process
    
    async def _mark_dynamics_message_sent(self, message_id: str, external_id: Optional[str] = None):
        """Mark Dynamics message as sent"""
        try:
            update_data = {
                'Sent': True,
                'SentAt': datetime.utcnow().isoformat(),
                'ModifiedOn': datetime.utcnow().isoformat()
            }
            
            # Store external ID in a custom field or metadata
            if external_id:
                # For now, we'll store it in a note or custom field
                # In production, you might want to add a field for this
                logger.info(f"External ID for message {message_id}: {external_id}")
            
            await self.dataverse.update_record('cre92_scheduledmessage', message_id, update_data)
            
            logger.info("Marked Dynamics message as sent", message_id=message_id)
            
        except Exception as e:
            logger.error("Failed to mark Dynamics message as sent", 
                        message_id=message_id, 
                        error=str(e))
            raise
    
    async def _mark_dynamics_message_failed(self, message_id: str, error_message: str):
        """Mark Dynamics message as failed"""
        try:
            update_data = {
                'Sent': False,
                'ModifiedOn': datetime.utcnow().isoformat()
                # Note: You might want to add an error field to your table
            }
            
            await self.dataverse.update_record('cre92_scheduledmessage', message_id, update_data)
            
            logger.info("Marked Dynamics message as failed", 
                       message_id=message_id, 
                       error=error_message)
            
        except Exception as e:
            logger.error("Failed to mark Dynamics message as failed", 
                        message_id=message_id, 
                        error=str(e))
            # Don't raise - we don't want to fail the whole process if marking failed

class DynamicsMessageProcessorCLI:
    """CLI interface for Dynamics message processor"""
    
    def __init__(self):
        self.processor = DynamicsMessageProcessor()
    
    async def process_messages(self, dry_run: bool = True) -> Dict[str, Any]:
        """Process Dynamics messages"""
        return await self.processor.process_dynamics_messages(dry_run=dry_run)
    
    async def test_processing(self) -> Dict[str, Any]:
        """Test Dynamics message processing with sample data"""
        # Create test Dynamics messages in sandbox
        test_messages = [
            {
                'MessageID': 'test-dynamics-1',
                'ClientName': 'Test Client 1',
                'Email': 'test1@example.com',
                'MessageStatus': 'Revised',
                'MessageSubject': 'Test Email from Dynamics',
                'MessageText': 'This is a test email message from Dynamics.',
                'MessageType': 'email',
                'ScheduledTimestamp': datetime.utcnow().isoformat(),
                'Sent': False
            },
            {
                'MessageID': 'test-dynamics-2',
                'ClientName': 'Test Client 2',
                'Email': 'test2@example.com',
                'MessageStatus': 2,  # Revised as integer
                'MessageSubject': 'Another Test Email',
                'MessageText': 'This is another test email from Dynamics.',
                'MessageType': 'email',
                'ScheduledTimestamp': datetime.utcnow().isoformat(),
                'Sent': False
            }
        ]
        
        # Add test messages to sandbox
        for message in test_messages:
            await self.processor.dataverse.create_record('cre92_scheduledmessage', message)
        
        # Process messages
        result = await self.processor.process_dynamics_messages(dry_run=True)
        
        return result

# Global Dynamics message processor instance
dynamics_message_processor = DynamicsMessageProcessor()
dynamics_message_processor_cli = DynamicsMessageProcessorCLI()
