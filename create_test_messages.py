#!/usr/bin/env python3
"""
Create test scheduled messages for the dashboard
"""

import asyncio
import os
from datetime import datetime, timedelta
from utils.sandbox import get_sandbox_dataverse

async def create_test_messages():
    """Create test scheduled messages in sandbox"""
    
    # Initialize sandbox dataverse
    dataverse = get_sandbox_dataverse()
    
    # Test messages for different channels
    test_messages = [
        # Email messages
        {
            'session_id': 'session-email-1',
            'client_id': 'client-1',
            'message_type': 'email',
            'recipient': 'client1@example.com',
            'subject': 'Session Follow-up',
            'body': 'Thank you for your session today. Here are your next steps...',
            'template': 'session_followup',
            'send_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'status': 'revised'
        },
        {
            'session_id': 'session-email-2',
            'client_id': 'client-2',
            'message_type': 'email',
            'recipient': 'client2@example.com',
            'subject': 'Appointment Reminder',
            'body': 'This is a reminder of your upcoming appointment tomorrow at 2 PM.',
            'template': 'appointment_reminder',
            'send_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'status': 'revised'
        },
        {
            'session_id': 'session-email-3',
            'client_id': 'client-3',
            'message_type': 'email',
            'recipient': 'client3@example.com',
            'subject': 'Welcome to Our Service',
            'body': 'Welcome! We\'re excited to have you on board.',
            'template': 'welcome',
            'send_time': datetime.utcnow().isoformat(),
            'status': 'sent'
        },
        
        # SMS messages
        {
            'session_id': 'session-sms-1',
            'client_id': 'client-4',
            'message_type': 'sms',
            'recipient': '+1234567890',
            'body': 'Your appointment is confirmed for tomorrow at 2 PM.',
            'template': 'sms_confirmation',
            'send_time': (datetime.utcnow() + timedelta(hours=3)).isoformat(),
            'status': 'revised'
        },
        {
            'session_id': 'session-sms-2',
            'client_id': 'client-5',
            'message_type': 'sms',
            'recipient': '+1987654321',
            'body': 'Quick reminder: Your session starts in 30 minutes.',
            'template': 'sms_reminder',
            'send_time': datetime.utcnow().isoformat(),
            'status': 'failed'
        },
        
        # Teams messages
        {
            'session_id': 'session-teams-1',
            'client_id': 'client-6',
            'message_type': 'teams',
            'channel_id': 'general',
            'body': 'New client onboarding completed. Please review the case.',
            'template': 'teams_notification',
            'send_time': (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            'status': 'revised'
        },
        
        # Telegram messages
        {
            'session_id': 'session-telegram-1',
            'client_id': 'client-7',
            'message_type': 'telegram',
            'chat_id': '123456789',
            'body': 'Your session notes are ready. Check your email for details.',
            'template': 'telegram_notification',
            'send_time': (datetime.utcnow() + timedelta(hours=4)).isoformat(),
            'status': 'revised'
        },
        
        # WhatsApp messages
        {
            'session_id': 'session-whatsapp-1',
            'client_id': 'client-8',
            'message_type': 'whatsapp',
            'recipient': '+1555123456',
            'body': 'Hi! Your appointment has been rescheduled to 3 PM today.',
            'template': 'whatsapp_reschedule',
            'send_time': (datetime.utcnow() + timedelta(hours=5)).isoformat(),
            'status': 'revised'
        }
    ]
    
    print("📨 Creating test scheduled messages...")
    
    created_count = 0
    for message in test_messages:
        try:
            await dataverse.create_record('scheduled_messages', message)
            created_count += 1
            print(f"✅ Created {message['message_type']} message for {message.get('recipient', message.get('chat_id', 'N/A'))}")
        except Exception as e:
            print(f"❌ Failed to create message: {e}")
    
    print(f"\n🎉 Created {created_count} test messages!")
    
    # Create some message logs
    print("\n📝 Creating test message logs...")
    
    test_logs = [
        {
            'message_id': 'test-log-1',
            'message_type': 'email',
            'recipient': 'client3@example.com',
            'subject': 'Welcome to Our Service',
            'body': 'Welcome! We\'re excited to have you on board.',
            'status': 'sent',
            'sent_at': datetime.utcnow().isoformat(),
            'provider': 'graph',
            'message_id_external': 'graph_email_123456'
        },
        {
            'message_id': 'test-log-2',
            'message_type': 'sms',
            'recipient': '+1987654321',
            'body': 'Quick reminder: Your session starts in 30 minutes.',
            'status': 'failed',
            'sent_at': datetime.utcnow().isoformat(),
            'provider': 'respond',
            'message_id_external': 'respond_sms_789012',
            'error_message': 'Invalid phone number format'
        }
    ]
    
    log_count = 0
    for log in test_logs:
        try:
            await dataverse.create_record('messages_log', log)
            log_count += 1
            print(f"✅ Created log entry for {log['message_type']} message")
        except Exception as e:
            print(f"❌ Failed to create log: {e}")
    
    print(f"\n🎉 Created {log_count} test log entries!")
    print("\n🚀 Ready to test the dashboard!")

if __name__ == "__main__":
    asyncio.run(create_test_messages())
