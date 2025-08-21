"""
Messaging Service Abstraction Layer

Provides a unified interface for different messaging providers:
- Microsoft Graph API (Teams, Email)
- Respond.io (Telegram, SMS, WhatsApp)
- Future: Custom providers
"""

from .base import MessagingProvider, MessageResult
from .graph_provider import GraphMessagingProvider
from .respond_provider import RespondMessagingProvider
from .factory import MessagingFactory

__all__ = [
    'MessagingProvider',
    'MessageResult', 
    'GraphMessagingProvider',
    'RespondMessagingProvider',
    'MessagingFactory'
]
