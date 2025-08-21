"""
Message Processor Function

Replaces Power Automate script for processing scheduled messages from the queue.
Uses messaging factory for multi-channel support.
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

class MessageProcessor:
    """Processes scheduled messages from the queue"""
    
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
        
        logger.info("MessageProcessor initialized with messaging factory")
    
    @safe_operation(Classification.BUSINESS, "scheduled-message-process")
    async def process_scheduled_messages(self, run_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Process scheduled messages from the queue"""
        
        if not run_id:
            run_id = create_run_id("scheduled-message-process", Classification.BUSINESS)
        
        logger.info("Starting scheduled message processing", run_id=run_id, dry_run=dry_run)
        
        try:
            # Query pending messages
            messages = await self._query_pending_messages()
            
            if not messages:
                logger.info("No pending messages found", run_id=run_id)
                return {
                    'status': 'success',
                    'processed_count': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'run_id': run_id
                }
            
            logger.info(f"Found {len(messages)} pending messages", run_id=run_id)
            
            # Process each message
            results = []
            for message in messages:
                try:
                    result = await self._process_message(message, dry_run)
                    results.append(result)
                except Exception as e:
                    logger.error("Failed to process message", 
                               message_id=message.get('id'), 
                               error=str(e), 
                               run_id=run_id)
                    result = {
                        'status': 'failed',
                        'message_id': message.get('id'),
                        'error': str(e)
                    }
                    results.append(result)
                    
                    # Mark message as failed in Dataverse
                    if not dry_run:
                        await self._mark_message_failed(message.get('id'), str(e))
            
            # Calculate statistics
            success_count = len([r for r in results if r['status'] == 'success'])
            failed_count = len([r for r in results if r['status'] == 'failed'])
            
            logger.info("Message processing completed", 
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
            logger.error("Message processing failed", error=str(e), run_id=run_id)
            raise
    
    async def _query_pending_messages(self) -> List[Dict[str, Any]]:
        """Query pending messages from Dataverse"""
        try:
            # Query messages that are ready to send
            filter_query = "status eq 'revised' and send_time le utcNow()"
            
            messages = await self.dataverse.query_records(
                'scheduled_messages',
                filter=filter_query,
                orderby='send_time asc',
                top=50  # Process in batches
            )
            
            logger.info(f"Queried {len(messages)} pending messages")
            return messages
            
        except Exception as e:
            logger.error("Failed to query pending messages", error=str(e))
            raise
    
    async def _process_message(self, message: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Process a single message"""
        message_id = message.get('id')
        message_type = message.get('message_type', 'email')
        
        logger.info("Processing message", 
                   message_id=message_id, 
                   message_type=message_type, 
                   dry_run=dry_run)
        
        if dry_run:
            return {
                'status': 'dry_run',
                'message_id': message_id,
                'message_type': message_type,
                'recipient': message.get('recipient'),
                'subject': message.get('subject')
            }
        
        try:
            # Use messaging factory to send message
            result = await self.messaging_factory.send_message(message)
            
            if result.success:
                # Log to messages_log
                await self._log_message_sent(
                    message_id=message_id,
                    message_type=message_type,
                    recipient=message.get('recipient'),
                    subject=message.get('subject'),
                    body=message.get('body'),
                    provider=result.provider,
                    external_id=result.external_id
                )
                
                # Update message status to sent
                await self._mark_message_sent(message_id, result.external_id)
                
                return {
                    'status': 'success',
                    'message_id': message_id,
                    'message_type': message_type,
                    'external_id': result.external_id,
                    'provider': result.provider
                }
            else:
                # Mark message as failed
                await self._mark_message_failed(message_id, result.error_message)
                
                return {
                    'status': 'failed',
                    'message_id': message_id,
                    'message_type': message_type,
                    'error': result.error_message
                }
            
        except Exception as e:
            logger.error("Failed to process message", 
                        message_id=message_id, 
                        error=str(e))
            raise
    
    async def _log_message_sent(self, message_id: str, message_type: str, recipient: str, 
                               subject: Optional[str], body: str, provider: str, external_id: str):
        """Log sent message to messages_log table"""
        try:
            log_entry = {
                'message_id': message_id,
                'message_type': message_type,
                'recipient': recipient,
                'subject': subject,
                'body': body,
                'status': 'sent',
                'sent_at': datetime.utcnow().isoformat(),
                'provider': provider,
                'message_id_external': external_id
            }
            
            await self.dataverse.create_record('messages_log', log_entry)
            
            logger.info("Logged message sent", 
                       message_id=message_id, 
                       external_id=external_id)
            
        except Exception as e:
            logger.error("Failed to log message sent", 
                        message_id=message_id, 
                        error=str(e))
            # Don't raise - logging failure shouldn't fail the whole process
    
    async def _mark_message_sent(self, message_id: str, external_id: Optional[str] = None):
        """Mark message as sent in scheduled_messages table"""
        try:
            update_data = {
                'status': 'sent',
                'processed_time': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if external_id:
                update_data['metadata'] = json.dumps({'external_id': external_id})
            
            await self.dataverse.update_record('scheduled_messages', message_id, update_data)
            
            logger.info("Marked message as sent", message_id=message_id)
            
        except Exception as e:
            logger.error("Failed to mark message as sent", 
                        message_id=message_id, 
                        error=str(e))
            raise
    
    async def _mark_message_failed(self, message_id: str, error_message: str):
        """Mark message as failed in scheduled_messages table"""
        try:
            update_data = {
                'status': 'failed',
                'error_message': error_message,
                'processed_time': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            await self.dataverse.update_record('scheduled_messages', message_id, update_data)
            
            logger.info("Marked message as failed", 
                       message_id=message_id, 
                       error=error_message)
            
        except Exception as e:
            logger.error("Failed to mark message as failed", 
                        message_id=message_id, 
                        error=str(e))
            # Don't raise - we don't want to fail the whole process if marking failed

class MessageProcessorCLI:
    """CLI interface for message processor"""
    
    def __init__(self):
        self.processor = MessageProcessor()
    
    async def process_messages(self, dry_run: bool = True) -> Dict[str, Any]:
        """Process scheduled messages"""
        return await self.processor.process_scheduled_messages(dry_run=dry_run)
    
    async def test_processing(self) -> Dict[str, Any]:
        """Test message processing with sample data"""
        # Create test messages in sandbox for all channels
        test_messages = [
            {
                'session_id': 'test-session-1',
                'client_id': 'test-client-1',
                'message_type': 'email',
                'recipient': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email message.',
                'send_time': datetime.utcnow().isoformat(),
                'status': 'revised'
            },
            {
                'session_id': 'test-session-2',
                'client_id': 'test-client-2',
                'message_type': 'sms',
                'recipient': '+1234567890',
                'body': 'This is a test SMS message.',
                'send_time': datetime.utcnow().isoformat(),
                'status': 'revised'
            },
            {
                'session_id': 'test-session-3',
                'client_id': 'test-client-3',
                'message_type': 'teams',
                'channel_id': 'test-channel-123',
                'body': 'This is a test Teams message.',
                'send_time': datetime.utcnow().isoformat(),
                'status': 'revised'
            },
            {
                'session_id': 'test-session-4',
                'client_id': 'test-client-4',
                'message_type': 'telegram',
                'chat_id': 'test-chat-456',
                'body': 'This is a test Telegram message.',
                'send_time': datetime.utcnow().isoformat(),
                'status': 'revised'
            },
            {
                'session_id': 'test-session-5',
                'client_id': 'test-client-5',
                'message_type': 'whatsapp',
                'recipient': '+1234567890',
                'body': 'This is a test WhatsApp message.',
                'send_time': datetime.utcnow().isoformat(),
                'status': 'revised'
            }
        ]
        
        # Add test messages to sandbox
        for message in test_messages:
            await self.processor.dataverse.create_record('scheduled_messages', message)
        
        # Process messages
        result = await self.processor.process_scheduled_messages(dry_run=True)
        
        return result

# Global message processor instance
message_processor = MessageProcessor()
message_processor_cli = MessageProcessorCLI()
