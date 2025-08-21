"""
Local Sandbox Mode

Provides mock services for safe development and testing without touching real data.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

logger = structlog.get_logger()

class MockDataverse:
    """Mock Dataverse service for local development"""
    
    def __init__(self):
        self.data = {
            'accounts': [],
            'contacts': [],
            'opportunities': [],
            'ai_conversations': [],
            'ai_projects': [],
            'ai_knowledge': []
        }
        logger.info("MockDataverse initialized")
    
    async def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock record"""
        record_id = f"{table_name}_{len(self.data.get(table_name, [])) + 1}"
        record = {
            'id': record_id,
            **data,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if table_name not in self.data:
            self.data[table_name] = []
        
        self.data[table_name].append(record)
        logger.info("Created mock record", table=table_name, id=record_id)
        return record
    
    async def query_records(self, table_name: str, filter: str = None, orderby: str = None, top: int = None) -> List[Dict[str, Any]]:
        """Query mock records"""
        records = self.data.get(table_name, [])
        
        # Simple mock filtering (in real implementation, this would be more sophisticated)
        if filter:
            logger.info("Mock filtering applied", filter=filter)
        
        if orderby:
            logger.info("Mock ordering applied", orderby=orderby)
        
        if top:
            records = records[:top]
        
        logger.info("Queried mock records", table=table_name, count=len(records))
        return records
    
    async def update_record(self, table_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a mock record"""
        records = self.data.get(table_name, [])
        for record in records:
            if record['id'] == record_id:
                record.update(data)
                record['updated_at'] = datetime.utcnow().isoformat()
                logger.info("Updated mock record", table=table_name, id=record_id)
                return record
        
        raise ValueError(f"Record {record_id} not found in {table_name}")
    
    async def delete_record(self, table_name: str, record_id: str) -> bool:
        """Delete a mock record"""
        records = self.data.get(table_name, [])
        for i, record in enumerate(records):
            if record['id'] == record_id:
                del records[i]
                logger.info("Deleted mock record", table=table_name, id=record_id)
                return True
        
        return False

class MockGraphAPI:
    """Mock Microsoft Graph API for local development"""
    
    def __init__(self):
        self.users = [
            {
                'id': 'user-1',
                'displayName': 'Dr. Benjamin F. Armstrong III',
                'mail': 'ben@example.com',
                'userPrincipalName': 'ben@example.com'
            }
        ]
        self.emails = []
        self.calendar_events = []
        logger.info("MockGraphAPI initialized")
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get mock users"""
        logger.info("Retrieved mock users", count=len(self.users))
        return self.users
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific mock user"""
        for user in self.users:
            if user['id'] == user_id:
                logger.info("Retrieved mock user", user_id=user_id)
                return user
        return None
    
    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a mock email"""
        email = {
            'id': f"email_{len(self.emails) + 1}",
            'to': to,
            'subject': subject,
            'body': body,
            'sent_at': datetime.utcnow().isoformat()
        }
        self.emails.append(email)
        logger.info("Sent mock email", to=to, subject=subject)
        return email
    
    async def get_calendar_events(self, user_id: str) -> List[Dict[str, Any]]:
        """Get mock calendar events"""
        logger.info("Retrieved mock calendar events", user_id=user_id, count=len(self.calendar_events))
        return self.calendar_events

class MockLLM:
    """Mock LLM service for local development"""
    
    def __init__(self):
        self.conversations = []
        self.providers = ['azure_openai', 'google_ai', 'anthropic', 'openai']
        self.models = ['gpt-4', 'gpt-3.5', 'gemini-pro', 'claude-3']
        logger.info("MockLLM initialized")
    
    async def generate_response(self, prompt: str, model: str = 'gpt-4', provider: str = 'azure_openai') -> str:
        """Generate a mock LLM response"""
        response = f"This is a mock response from {provider} using {model}. You said: {prompt[:50]}..."
        
        conversation = {
            'id': f"conv_{len(self.conversations) + 1}",
            'prompt': prompt,
            'response': response,
            'model': model,
            'provider': provider,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.conversations.append(conversation)
        
        logger.info("Generated mock LLM response", model=model, provider=provider)
        return response
    
    async def get_models(self, provider: str = None) -> List[str]:
        """Get available mock models"""
        if provider:
            return [model for model in self.models if provider in model.lower()]
        return self.models
    
    async def get_providers(self) -> List[str]:
        """Get available mock providers"""
        return self.providers

class MockEmailService:
    """Mock email service for local development"""
    
    def __init__(self):
        self.sent_emails = []
        logger.info("MockEmailService initialized")
    
    async def send_email(self, to: str, subject: str, body: str, template: str = None) -> Dict[str, Any]:
        """Send a mock email"""
        email = {
            'id': f"email_{len(self.sent_emails) + 1}",
            'to': to,
            'subject': subject,
            'body': body,
            'template': template,
            'sent_at': datetime.utcnow().isoformat(),
            'status': 'sent'
        }
        self.sent_emails.append(email)
        
        logger.info("Sent mock email", to=to, subject=subject, template=template)
        return email
    
    async def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent mock emails"""
        return self.sent_emails.copy()

class SandboxManager:
    """Manages local sandbox mode"""
    
    def __init__(self):
        self.enabled = os.getenv("BLC_LOCAL_SANDBOX", "false").lower() == "true"
        self.dataverse = MockDataverse()
        self.graph_api = MockGraphAPI()
        self.llm = MockLLM()
        self.email_service = MockEmailService()
        
        logger.info("SandboxManager initialized", enabled=self.enabled)
    
    def is_enabled(self) -> bool:
        """Check if sandbox mode is enabled"""
        return self.enabled
    
    async def reset_data(self):
        """Reset all mock data"""
        self.dataverse = MockDataverse()
        self.graph_api = MockGraphAPI()
        self.llm = MockLLM()
        self.email_service = MockEmailService()
        logger.info("Reset all mock data")
    
    async def export_data(self, filepath: str):
        """Export mock data to file"""
        data = {
            'dataverse': self.dataverse.data,
            'graph_api': {
                'users': self.graph_api.users,
                'emails': self.graph_api.emails,
                'calendar_events': self.graph_api.calendar_events
            },
            'llm': {
                'conversations': self.llm.conversations
            },
            'email_service': {
                'sent_emails': self.email_service.sent_emails
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Exported mock data", filepath=filepath)
    
    async def import_data(self, filepath: str):
        """Import mock data from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if 'dataverse' in data:
            self.dataverse.data = data['dataverse']
        
        if 'graph_api' in data:
            self.graph_api.users = data['graph_api'].get('users', [])
            self.graph_api.emails = data['graph_api'].get('emails', [])
            self.graph_api.calendar_events = data['graph_api'].get('calendar_events', [])
        
        if 'llm' in data:
            self.llm.conversations = data['llm'].get('conversations', [])
        
        if 'email_service' in data:
            self.email_service.sent_emails = data['email_service'].get('sent_emails', [])
        
        logger.info("Imported mock data", filepath=filepath)

# Global sandbox manager instance
sandbox_manager = SandboxManager()

def get_sandbox_dataverse():
    """Get sandbox Dataverse if enabled, otherwise return None"""
    if sandbox_manager.is_enabled():
        return sandbox_manager.dataverse
    return None

def get_sandbox_graph_api():
    """Get sandbox Graph API if enabled, otherwise return None"""
    if sandbox_manager.is_enabled():
        return sandbox_manager.graph_api
    return None

def get_sandbox_llm():
    """Get sandbox LLM if enabled, otherwise return None"""
    if sandbox_manager.is_enabled():
        return sandbox_manager.llm
    return None

def get_sandbox_email_service():
    """Get sandbox email service if enabled, otherwise return None"""
    if sandbox_manager.is_enabled():
        return sandbox_manager.email_service
    return None
