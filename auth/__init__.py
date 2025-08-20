"""
Authentication module for Life Cockpit.

Provides authentication managers for Microsoft Graph API and Dataverse Web API.
"""

from .graph import GraphAuthManager
from .dataverse import DataverseAuthManager

__all__ = ['GraphAuthManager', 'DataverseAuthManager']
