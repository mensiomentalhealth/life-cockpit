"""
Azure Functions for Life Cockpit

Serverless functions called by Logic Apps to replace Power Automate functionality.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import structlog
from utils.guardrails import safe_operation, Classification, create_run_id

logger = structlog.get_logger()

class AzureFunction:
    """Base class for Azure Functions"""
    
    def __init__(self, name: str):
        self.name = name
        self.function_url = os.getenv(f"AZURE_FUNCTION_{name.upper()}_URL")
        self.function_key = os.getenv(f"AZURE_FUNCTION_{name.upper()}_KEY")
        
        logger.info(f"Azure Function initialized", name=name, url=self.function_url)
    
    async def invoke(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the Azure Function"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "x-functions-key": self.function_key
                }
                
                response = await client.post(
                    self.function_url,
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to invoke function {self.name}", error=str(e))
            raise

class DataverseWebhookFunction(AzureFunction):
    """Function to handle Dataverse webhooks"""
    
    def __init__(self):
        super().__init__("dataverse_webhook")
    
    @safe_operation(Classification.BUSINESS, "dataverse-webhook-process")
    async def process_webhook(self, entity: str, operation: str, data: Dict[str, Any], run_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """Process a Dataverse webhook"""
        
        if dry_run:
            logger.info("Processing webhook in dry-run mode", 
                       entity=entity, operation=operation, run_id=run_id)
            return {
                'status': 'dry_run',
                'entity': entity,
                'operation': operation,
                'processed': True
            }
        
        try:
            # Process the webhook based on entity and operation
            if entity == "accounts":
                result = await self._process_account_webhook(operation, data)
            elif entity == "contacts":
                result = await self._process_contact_webhook(operation, data)
            elif entity == "opportunities":
                result = await self._process_opportunity_webhook(operation, data)
            else:
                result = await self._process_generic_webhook(entity, operation, data)
            
            logger.info("Webhook processed successfully", 
                       entity=entity, operation=operation, run_id=run_id)
            
            return {
                'status': 'success',
                'entity': entity,
                'operation': operation,
                'result': result
            }
            
        except Exception as e:
            logger.error("Failed to process webhook", 
                        entity=entity, operation=operation, error=str(e), run_id=run_id)
            raise
    
    async def _process_account_webhook(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process account-related webhooks"""
        if operation == "Create":
            # Handle new account creation
            return await self._handle_new_account(data)
        elif operation == "Update":
            # Handle account updates
            return await self._handle_account_update(data)
        elif operation == "Delete":
            # Handle account deletion
            return await self._handle_account_deletion(data)
        else:
            return {'action': 'none', 'reason': f'Unknown operation: {operation}'}
    
    async def _process_contact_webhook(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process contact-related webhooks"""
        if operation == "Create":
            return await self._handle_new_contact(data)
        elif operation == "Update":
            return await self._handle_contact_update(data)
        else:
            return {'action': 'none', 'reason': f'Unknown operation: {operation}'}
    
    async def _process_opportunity_webhook(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process opportunity-related webhooks"""
        if operation == "Create":
            return await self._handle_new_opportunity(data)
        elif operation == "Update":
            return await self._handle_opportunity_update(data)
        else:
            return {'action': 'none', 'reason': f'Unknown operation: {operation}'}
    
    async def _process_generic_webhook(self, entity: str, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic webhooks"""
        logger.info("Processing generic webhook", entity=entity, operation=operation)
        return {
            'action': 'logged',
            'entity': entity,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Handler methods for specific webhook types
    async def _handle_new_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new account creation"""
        # Add your account creation logic here
        return {'action': 'account_created', 'account_id': data.get('accountid')}
    
    async def _handle_account_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle account updates"""
        # Add your account update logic here
        return {'action': 'account_updated', 'account_id': data.get('accountid')}
    
    async def _handle_account_deletion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle account deletion"""
        # Add your account deletion logic here
        return {'action': 'account_deleted', 'account_id': data.get('accountid')}
    
    async def _handle_new_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new contact creation"""
        # Add your contact creation logic here
        return {'action': 'contact_created', 'contact_id': data.get('contactid')}
    
    async def _handle_contact_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle contact updates"""
        # Add your contact update logic here
        return {'action': 'contact_updated', 'contact_id': data.get('contactid')}
    
    async def _handle_new_opportunity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new opportunity creation"""
        # Add your opportunity creation logic here
        return {'action': 'opportunity_created', 'opportunity_id': data.get('opportunityid')}
    
    async def _handle_opportunity_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opportunity updates"""
        # Add your opportunity update logic here
        return {'action': 'opportunity_updated', 'opportunity_id': data.get('opportunityid')}

class EmailAutomationFunction(AzureFunction):
    """Function to handle email automation"""
    
    def __init__(self):
        super().__init__("email_automation")
    
    @safe_operation(Classification.BUSINESS, "email-automation-send")
    async def send_email(self, to: str, subject: str, body: str, template: Optional[str] = None, run_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Send an automated email"""
        
        if dry_run:
            logger.info("Sending email in dry-run mode", 
                       to=to, subject=subject, run_id=run_id)
            return {
                'status': 'dry_run',
                'to': to,
                'subject': subject,
                'sent': False
            }
        
        try:
            # Process email template if provided
            if template:
                body = await self._process_template(template, body)
            
            # Send email (integrate with your email service)
            result = await self._send_email_via_service(to, subject, body)
            
            logger.info("Email sent successfully", 
                       to=to, subject=subject, run_id=run_id)
            
            return {
                'status': 'success',
                'to': to,
                'subject': subject,
                'sent': True,
                'message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error("Failed to send email", 
                        to=to, subject=subject, error=str(e), run_id=run_id)
            raise
    
    async def _process_template(self, template: str, data: str) -> str:
        """Process email template"""
        # Add your template processing logic here
        # This could use Jinja2 or similar templating engine
        return data
    
    async def _send_email_via_service(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email via email service (SendGrid, SMTP, etc.)"""
        # Add your email service integration here
        # For now, return mock response
        return {
            'message_id': f"msg_{datetime.utcnow().timestamp()}",
            'status': 'sent'
        }

class ScheduledTaskFunction(AzureFunction):
    """Function to handle scheduled tasks"""
    
    def __init__(self):
        super().__init__("scheduled_task")
    
    @safe_operation(Classification.PERSONAL, "scheduled-task-execute")
    async def execute_task(self, task: str, run_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Execute a scheduled task"""
        
        if dry_run:
            logger.info("Executing task in dry-run mode", 
                       task=task, run_id=run_id)
            return {
                'status': 'dry_run',
                'task': task,
                'executed': False
            }
        
        try:
            # Execute task based on type
            if task == "daily_backup":
                result = await self._execute_daily_backup()
            elif task == "data_cleanup":
                result = await self._execute_data_cleanup()
            elif task == "report_generation":
                result = await self._execute_report_generation()
            else:
                result = await self._execute_generic_task(task)
            
            logger.info("Task executed successfully", 
                       task=task, run_id=run_id)
            
            return {
                'status': 'success',
                'task': task,
                'executed': True,
                'result': result
            }
            
        except Exception as e:
            logger.error("Failed to execute task", 
                        task=task, error=str(e), run_id=run_id)
            raise
    
    async def _execute_daily_backup(self) -> Dict[str, Any]:
        """Execute daily backup task"""
        # Add your backup logic here
        return {'action': 'backup_completed', 'timestamp': datetime.utcnow().isoformat()}
    
    async def _execute_data_cleanup(self) -> Dict[str, Any]:
        """Execute data cleanup task"""
        # Add your data cleanup logic here
        return {'action': 'cleanup_completed', 'timestamp': datetime.utcnow().isoformat()}
    
    async def _execute_report_generation(self) -> Dict[str, Any]:
        """Execute report generation task"""
        # Add your report generation logic here
        return {'action': 'report_generated', 'timestamp': datetime.utcnow().isoformat()}
    
    async def _execute_generic_task(self, task: str) -> Dict[str, Any]:
        """Execute generic task"""
        logger.info("Executing generic task", task=task)
        return {
            'action': 'task_executed',
            'task': task,
            'timestamp': datetime.utcnow().isoformat()
        }

class FunctionsManager:
    """Manages all Azure Functions"""
    
    def __init__(self):
        self.dataverse_webhook = DataverseWebhookFunction()
        self.email_automation = EmailAutomationFunction()
        self.scheduled_task = ScheduledTaskFunction()
        
        logger.info("FunctionsManager initialized")
    
    async def process_dataverse_webhook(self, entity: str, operation: str, data: Dict[str, Any], run_id: str = None) -> Dict[str, Any]:
        """Process a Dataverse webhook"""
        return await self.dataverse_webhook.process_webhook(entity, operation, data, run_id)
    
    async def send_email(self, to: str, subject: str, body: str, template: Optional[str] = None, run_id: str = None) -> Dict[str, Any]:
        """Send an automated email"""
        return await self.email_automation.send_email(to, subject, body, template, run_id)
    
    async def execute_scheduled_task(self, task: str, run_id: str = None) -> Dict[str, Any]:
        """Execute a scheduled task"""
        return await self.scheduled_task.execute_task(task, run_id)

# Global functions manager instance
functions_manager = FunctionsManager()
