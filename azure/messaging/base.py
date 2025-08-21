"""
Base classes for messaging providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger()

@dataclass
class MessageResult:
    """Result from sending a message"""
    success: bool
    external_id: Optional[str] = None
    provider: Optional[str] = None
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessagingProvider(ABC):
    """Abstract base class for messaging providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__
        logger.info(f"Initialized {self.provider_name}")
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> MessageResult:
        """Send a message via this provider"""
        pass
    
    @abstractmethod
    async def get_message_status(self, external_id: str) -> MessageResult:
        """Get the status of a sent message"""
        pass
    
    @abstractmethod
    def supports_message_type(self, message_type: str) -> bool:
        """Check if this provider supports the given message type"""
        pass
    
    async def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message before sending"""
        required_fields = self.get_required_fields(message.get('message_type', 'unknown'))
        
        for field in required_fields:
            if field not in message or not message[field]:
                logger.error(f"Missing required field: {field}", 
                           message_type=message.get('message_type'),
                           provider=self.provider_name)
                return False
        
        return True
    
    def get_required_fields(self, message_type: str) -> List[str]:
        """Get required fields for a message type"""
        base_fields = ['message_type', 'body']
        
        type_specific_fields = {
            'email': ['recipient', 'subject'],
            'sms': ['recipient'],
            'teams': ['channel_id'],
            'telegram': ['chat_id'],
            'whatsapp': ['recipient']
        }
        
        return base_fields + type_specific_fields.get(message_type, [])
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        try:
            # Basic health check - can be overridden by providers
            return True
        except Exception as e:
            logger.error(f"Health check failed for {self.provider_name}", error=str(e))
            return False
