"""
Messaging Factory

Manages multiple messaging providers and routes messages to the appropriate one
"""

from typing import Dict, Any, List, Optional
import structlog
from .base import MessagingProvider, MessageResult
from .graph_provider import GraphMessagingProvider
from .respond_provider import RespondMessagingProvider

logger = structlog.get_logger()

class MessagingFactory:
    """Factory for managing multiple messaging providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, MessagingProvider] = {}
        self._initialize_providers()
        
        logger.info(f"Initialized MessagingFactory with {len(self.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        # Initialize Graph provider for Teams and Email
        if 'graph' in self.config:
            self.providers['graph'] = GraphMessagingProvider(self.config['graph'])
        
        # Initialize Respond.io provider for Telegram, SMS, WhatsApp
        if 'respond' in self.config:
            self.providers['respond'] = RespondMessagingProvider(self.config['respond'])
        
        # Future: Add more providers here
        # if 'custom' in self.config:
        #     self.providers['custom'] = CustomMessagingProvider(self.config['custom'])
    
    def get_provider_for_message_type(self, message_type: str) -> Optional[MessagingProvider]:
        """Get the appropriate provider for a message type"""
        for provider in self.providers.values():
            if provider.supports_message_type(message_type):
                return provider
        
        logger.error(f"No provider found for message type: {message_type}")
        return None
    
    async def send_message(self, message: Dict[str, Any]) -> MessageResult:
        """Send a message via the appropriate provider"""
        message_type = message.get('message_type')
        
        if not message_type:
            return MessageResult(
                success=False,
                error_message="Message type is required"
            )
        
        provider = self.get_provider_for_message_type(message_type)
        if not provider:
            return MessageResult(
                success=False,
                error_message=f"No provider available for message type: {message_type}"
            )
        
        logger.info(f"Routing {message_type} message to {provider.provider_name}")
        return await provider.send_message(message)
    
    async def get_message_status(self, external_id: str, provider_name: str) -> MessageResult:
        """Get message status from a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return MessageResult(
                success=False,
                error_message=f"Provider not found: {provider_name}"
            )
        
        return await provider.get_message_status(external_id)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        
        for name, provider in self.providers.items():
            try:
                health_status[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}", error=str(e))
                health_status[name] = False
        
        return health_status
    
    def get_supported_message_types(self) -> Dict[str, List[str]]:
        """Get all supported message types by provider"""
        supported_types = {}
        
        for name, provider in self.providers.items():
            supported_types[name] = []
            for message_type in ['email', 'sms', 'teams', 'telegram', 'whatsapp']:
                if provider.supports_message_type(message_type):
                    supported_types[name].append(message_type)
        
        return supported_types
    
    def add_provider(self, name: str, provider: MessagingProvider):
        """Add a new provider dynamically"""
        self.providers[name] = provider
        logger.info(f"Added new provider: {name}")
    
    def remove_provider(self, name: str):
        """Remove a provider"""
        if name in self.providers:
            del self.providers[name]
            logger.info(f"Removed provider: {name}")
        else:
            logger.warning(f"Provider not found: {name}")
    
    def list_providers(self) -> List[str]:
        """List all available providers"""
        return list(self.providers.keys())
