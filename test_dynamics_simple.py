#!/usr/bin/env python3
"""
Simple Dynamics Message Processor Test (No Guardrails)
"""

import asyncio
import os
from datetime import datetime
from utils.sandbox import get_sandbox_dataverse
from azure.messaging import MessagingFactory

async def test_dynamics_simple():
    """Test Dynamics message processing without guardrails"""
    
    print("🧪 Testing Dynamics Message Processor (Simple)...")
    
    # Initialize services directly
    dataverse = get_sandbox_dataverse()
    
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
    
    messaging_factory = MessagingFactory(messaging_config)
    
    # Create test Dynamics messages
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
    print("📨 Creating test Dynamics messages...")
    for message in test_messages:
        await dataverse.create_record('cre92_scheduledmessage', message)
        print(f"✅ Created {message['MessageType']} message for {message['Email']}")
    
    # Query pending messages
    print("\n🔍 Querying pending messages...")
    filter_query = "(MessageStatus eq 'Revised' or MessageStatus eq 2) and ScheduledTimestamp le utcNow() and Sent eq false"
    messages = await dataverse.query_records('cre92_scheduledmessage', filter=filter_query)
    print(f"📊 Found {len(messages)} pending messages")
    
    # Process each message
    print("\n🚀 Processing messages...")
    results = []
    
    for message in messages:
        print(f"\n📧 Processing message {message['MessageID']}:")
        print(f"   Type: {message['MessageType']}")
        print(f"   To: {message['Email']}")
        print(f"   Subject: {message['MessageSubject']}")
        
        # Convert to messaging format
        messaging_message = {
            'message_type': message['MessageType'],
            'recipient': message['Email'],
            'subject': message['MessageSubject'],
            'body': message['MessageText']
        }
        
        # Send via messaging factory
        result = await messaging_factory.send_message(messaging_message)
        
        if result.success:
            print(f"   ✅ Sent successfully!")
            print(f"   Provider: {result.provider}")
            print(f"   External ID: {result.external_id}")
            
            # Update Dynamics record (use the actual record ID from sandbox)
            update_data = {
                'Sent': True,
                'SentAt': datetime.utcnow().isoformat(),
                'ModifiedOn': datetime.utcnow().isoformat()
            }
            # In sandbox, the actual ID is different from MessageID
            actual_record_id = message.get('id', message['MessageID'])
            await dataverse.update_record('cre92_scheduledmessage', actual_record_id, update_data)
            print(f"   📝 Updated Dynamics record")
            
            results.append({
                'message_id': message['MessageID'],
                'status': 'success',
                'provider': result.provider,
                'external_id': result.external_id
            })
        else:
            print(f"   ❌ Failed to send: {result.error_message}")
            results.append({
                'message_id': message['MessageID'],
                'status': 'failed',
                'error': result.error_message
            })
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Success: {len([r for r in results if r['status'] == 'success'])}")
    print(f"   Failed: {len([r for r in results if r['status'] == 'failed'])}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    # Set environment variables
    os.environ['BLC_LOCAL_SANDBOX'] = 'true'
    
    asyncio.run(test_dynamics_simple())
