#!/usr/bin/env python3
"""
Simple test script for messaging factory
"""

import asyncio
import os
from azure.messaging import MessagingFactory
from azure.message_processor import MessageProcessor

async def test_messaging_factory():
    """Test the messaging factory directly"""
    print("🧪 Testing Messaging Factory...")
    
    # Initialize messaging factory
    messaging_config = {
        'graph': {
            'tenant_id': 'mock-tenant',
            'client_id': 'mock-client',
            'client_secret': 'mock-secret'
        },
        'respond': {
            'api_key': 'mock-key',
            'workspace_id': 'mock-workspace',
            'base_url': 'https://api.respond.io'
        }
    }
    
    factory = MessagingFactory(messaging_config)
    
    # Test messages for each channel
    test_messages = [
        {
            'message_type': 'email',
            'recipient': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email message.'
        },
        {
            'message_type': 'teams',
            'channel_id': 'test-channel-123',
            'body': 'This is a test Teams message.'
        },
        {
            'message_type': 'sms',
            'recipient': '+1234567890',
            'body': 'This is a test SMS message.'
        },
        {
            'message_type': 'telegram',
            'chat_id': 'test-chat-456',
            'body': 'This is a test Telegram message.'
        },
        {
            'message_type': 'whatsapp',
            'recipient': '+1234567890',
            'body': 'This is a test WhatsApp message.'
        }
    ]
    
    print(f"📨 Testing {len(test_messages)} message types...")
    
    results = []
    for message in test_messages:
        print(f"\n🔍 Processing {message['message_type']} message...")
        result = await factory.send_message(message)
        
        if result.success:
            print(f"✅ {message['message_type'].upper()}: Success!")
            print(f"   Provider: {result.provider}")
            print(f"   External ID: {result.external_id}")
        else:
            print(f"❌ {message['message_type'].upper()}: Failed!")
            print(f"   Error: {result.error_message}")
        
        results.append(result)
    
    # Summary
    success_count = len([r for r in results if r.success])
    print(f"\n📊 Summary: {success_count}/{len(results)} messages sent successfully")
    
    # Show supported message types
    supported_types = factory.get_supported_message_types()
    print(f"\n🔧 Supported message types by provider:")
    for provider, types in supported_types.items():
        print(f"   {provider}: {', '.join(types)}")

async def test_message_processor():
    """Test the message processor (without guardrails)"""
    print("\n🧪 Testing Message Processor...")
    
    # Create a simple processor without guardrails
    processor = MessageProcessor()
    
    # Create test messages in memory (not sandbox)
    test_messages = [
        {
            'id': 'test-1',
            'session_id': 'test-session-1',
            'client_id': 'test-client-1',
            'message_type': 'email',
            'recipient': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email message.',
            'send_time': '2024-01-01T12:00:00Z',
            'status': 'revised'
        }
    ]
    
    print(f"📨 Processing {len(test_messages)} test message...")
    
    # Process each message directly
    for message in test_messages:
        print(f"\n🔍 Processing {message['message_type']} message...")
        
        # Use messaging factory directly
        result = await processor.messaging_factory.send_message(message)
        
        if result.success:
            print(f"✅ {message['message_type'].upper()}: Success!")
            print(f"   Provider: {result.provider}")
            print(f"   External ID: {result.external_id}")
        else:
            print(f"❌ {message['message_type'].upper()}: Failed!")
            print(f"   Error: {result.error_message}")

if __name__ == "__main__":
    print("🚀 Multi-Channel Messaging Factory Test")
    print("=" * 50)
    
    asyncio.run(test_messaging_factory())
    asyncio.run(test_message_processor())
    
    print("\n�� Test completed!")
