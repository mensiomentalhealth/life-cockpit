#!/usr/bin/env python3
"""
Multi-Channel Messaging Factory
Main entry point for the messaging system
"""

from azure.messaging.factory import MessagingFactory
from azure.messaging.base import MessageResult

__all__ = ['MessagingFactory', 'MessageResult']
