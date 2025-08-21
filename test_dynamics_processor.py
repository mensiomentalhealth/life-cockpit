#!/usr/bin/env python3
"""
Test Dynamics Message Processor
"""

import asyncio
import os
from datetime import datetime
from azure.dynamics_message_processor import dynamics_message_processor

async def test_dynamics_processor():
    """Test the Dynamics message processor directly"""
    
    print("🧪 Testing Dynamics Message Processor...")
    
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
        await dynamics_message_processor.dataverse.create_record('cre92_scheduledmessage', message)
        print(f"✅ Created {message['MessageType']} message for {message['Email']}")
    
    # Process messages (dry run first)
    print("\n🔍 Testing dry run...")
    wrapped_result = await dynamics_message_processor.process_dynamics_messages(dry_run=True)
    
    # Handle the wrapped result from safe_operation decorator
    if isinstance(wrapped_result, dict) and 'result' in wrapped_result:
        result = wrapped_result['result']
    else:
        result = wrapped_result
    
    print(f"📊 Dry run results:")
    print(f"   Processed: {result['processed_count']}")
    print(f"   Success: {result['success_count']}")
    print(f"   Failed: {result['failed_count']}")
    
    # Process messages (real run)
    print("\n🚀 Testing real processing...")
    wrapped_result = await dynamics_message_processor.process_dynamics_messages(dry_run=False)
    
    # Handle the wrapped result from safe_operation decorator
    if isinstance(wrapped_result, dict) and 'result' in wrapped_result:
        result = wrapped_result['result']
    else:
        result = wrapped_result
    
    print(f"📊 Real run results:")
    print(f"   Processed: {result['processed_count']}")
    print(f"   Success: {result['success_count']}")
    print(f"   Failed: {result['failed_count']}")
    
    if result['results']:
        print("\n📋 Detailed results:")
        for r in result['results']:
            print(f"   Message {r['message_id']}: {r['status']}")
            if r['status'] == 'success':
                print(f"     Provider: {r['provider']}")
                print(f"     External ID: {r['external_id']}")
            elif r['status'] == 'failed':
                print(f"     Error: {r['error']}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    # Set environment variables
    os.environ['BLC_LOCAL_SANDBOX'] = 'true'
    
    asyncio.run(test_dynamics_processor())
