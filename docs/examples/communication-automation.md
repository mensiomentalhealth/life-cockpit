# Communication Automation Guide

Life Cockpit's communication automation system handles multi-channel messaging including email, text messages, app notifications, and more.

## 🎯 Overview

The communication system is designed to be:
- **Multi-channel**: Email, SMS, Teams, Slack, push notifications
- **Template-driven**: Reusable message templates
- **Scheduled**: Time-based and event-triggered messaging
- **Tracked**: Full delivery and engagement tracking
- **Compliant**: Built-in compliance and audit features

## 📧 Email Automation

### Basic Email Sending

```python
from comms.email import EmailManager

# Initialize email manager
email_mgr = EmailManager()

# Send simple email
await email_mgr.send_email(
    to="client@example.com",
    subject="Session Reminder",
    body="Your session is tomorrow at 2 PM."
)
```

### Template-Based Emails

```python
# Load email template
template = await email_mgr.load_template("session_reminder")

# Send with template data
await email_mgr.send_template(
    template_name="session_reminder",
    to="client@example.com",
    data={
        "client_name": "John Doe",
        "session_date": "2025-08-21",
        "session_time": "2:00 PM",
        "session_type": "Follow-up"
    }
)
```

### Email Templates

**Session Reminder Template:**
```html
Subject: Session Reminder - {{session_date}}

Hi {{client_name}},

This is a reminder for your {{session_type}} session on {{session_date}} at {{session_time}}.

Please prepare:
- Any questions or concerns
- Updates on your progress
- Topics you'd like to discuss

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
Your Life Cockpit Team
```

### Email Scheduling

```python
# Schedule email for later
await email_mgr.schedule_email(
    to="client@example.com",
    subject="Follow-up Survey",
    body="How was your session?",
    send_at="2025-08-22T10:00:00Z"
)

# Schedule recurring emails
await email_mgr.schedule_recurring(
    template_name="weekly_checkin",
    to="client@example.com",
    frequency="weekly",
    start_date="2025-08-21",
    end_date="2025-12-31"
)
```

## 📱 SMS/Text Messaging

### Basic SMS Sending

```python
from comms.sms import SMSManager

sms_mgr = SMSManager()

# Send SMS
await sms_mgr.send_sms(
    to="+1234567890",
    message="Your session reminder: Tomorrow at 2 PM"
)
```

### SMS Templates

```python
# Send template-based SMS
await sms_mgr.send_template(
    template_name="urgent_reminder",
    to="+1234567890",
    data={
        "client_name": "John",
        "session_time": "2 PM",
        "minutes_until": "30"
    }
)
```

**SMS Template:**
```
Hi {{client_name}}, your session starts in {{minutes_until}} minutes. 
Please join the meeting room.
```

## 💬 Teams/Slack Integration

### Teams Messages

```python
from comms.teams import TeamsManager

teams_mgr = TeamsManager()

# Send to Teams channel
await teams_mgr.send_message(
    channel="general",
    message="New client session scheduled for tomorrow"
)
```

### Rich Cards

```python
# Send rich card with actions
await teams_mgr.send_card(
    channel="notifications",
    title="Session Reminder",
    text="Client session starting in 15 minutes",
    actions=[
        {"type": "openUrl", "title": "Join Meeting", "url": "https://meet.example.com"},
        {"type": "openUrl", "title": "View Details", "url": "https://cockpit.example.com/session/123"}
    ]
)
```

## 🔔 Push Notifications

### App Notifications

```python
from comms.push import PushNotificationManager

push_mgr = PushNotificationManager()

# Send push notification
await push_mgr.send_notification(
    user_id="user123",
    title="Session Reminder",
    body="Your session starts in 15 minutes",
    data={"session_id": "123", "action": "join_meeting"}
)
```

### Batch Notifications

```python
# Send to multiple users
await push_mgr.send_batch(
    user_ids=["user1", "user2", "user3"],
    title="System Maintenance",
    body="Scheduled maintenance tonight at 2 AM",
    data={"maintenance_id": "456"}
)
```

## 📋 Unified Communication Workflows

### Multi-Channel Campaign

```python
from comms.campaign import CommunicationCampaign

# Create multi-channel campaign
campaign = CommunicationCampaign("session_reminder")

# Add communication channels
campaign.add_email(
    template="session_reminder",
    priority=1,
    delay_hours=24
)

campaign.add_sms(
    template="urgent_reminder",
    priority=2,
    delay_hours=1
)

campaign.add_push(
    template="immediate_reminder",
    priority=3,
    delay_minutes=15
)

# Execute campaign
await campaign.execute(
    user_id="client123",
    data={"session_time": "2:00 PM", "client_name": "John"}
)
```

### Conditional Communication

```python
# Smart communication based on user preferences
async def send_smart_reminder(client_id: str, session_data: dict):
    client_prefs = await get_client_preferences(client_id)
    
    if client_prefs.email_enabled:
        await email_mgr.send_template("session_reminder", client_prefs.email, session_data)
    
    if client_prefs.sms_enabled and client_prefs.urgent_only:
        await sms_mgr.send_template("urgent_reminder", client_prefs.phone, session_data)
    
    if client_prefs.push_enabled:
        await push_mgr.send_notification(client_id, "Session Reminder", session_data)
```

## 📊 Tracking and Analytics

### Delivery Tracking

```python
# Track message delivery
tracking_id = await comms_mgr.send_with_tracking(
    channel="email",
    to="client@example.com",
    template="session_reminder",
    data=session_data
)

# Check delivery status
status = await comms_mgr.get_delivery_status(tracking_id)
print(f"Status: {status.delivered}, Opened: {status.opened}, Clicked: {status.clicked}")
```

### Engagement Analytics

```python
# Get communication analytics
analytics = await comms_mgr.get_analytics(
    client_id="client123",
    date_range="last_30_days"
)

print(f"Emails sent: {analytics.emails_sent}")
print(f"Emails opened: {analytics.emails_opened}")
print(f"SMS delivered: {analytics.sms_delivered}")
print(f"Response rate: {analytics.response_rate}%")
```

## 🔄 Automation Triggers

### Event-Based Communication

```python
from comms.triggers import CommunicationTrigger

# Create trigger for new session
trigger = CommunicationTrigger("session_created")

@trigger.on("session_created")
async def handle_new_session(session_data: dict):
    # Send welcome email
    await email_mgr.send_template(
        "welcome_session",
        session_data["client_email"],
        session_data
    )
    
    # Schedule reminder
    await email_mgr.schedule_template(
        "session_reminder",
        session_data["client_email"],
        session_data,
        send_at=session_data["session_time"] - timedelta(hours=24)
    )
```

### Scheduled Communication

```python
# Daily digest emails
@comms_mgr.schedule_daily("09:00")
async def send_daily_digest():
    clients = await get_active_clients()
    
    for client in clients:
        digest_data = await generate_daily_digest(client.id)
        await email_mgr.send_template("daily_digest", client.email, digest_data)
```

## 🛡️ Compliance and Safety

### Opt-out Management

```python
# Check opt-out status
if await comms_mgr.is_opted_out(client_id, "email"):
    logger.info(f"Client {client_id} has opted out of emails")
    return

# Handle opt-out
await comms_mgr.opt_out(client_id, "email", reason="client_request")
```

### Rate Limiting

```python
# Rate-limited sending
await comms_mgr.send_with_rate_limit(
    channel="sms",
    to="+1234567890",
    message="Your reminder",
    max_per_hour=5,
    max_per_day=20
)
```

### Audit Logging

```python
# All communications are automatically logged
audit_log = await comms_mgr.get_audit_log(
    client_id="client123",
    date_range="last_7_days"
)

for entry in audit_log:
    print(f"{entry.timestamp}: {entry.channel} - {entry.status}")
```

## 🎨 Template Management

### Template Variables

```python
# Available template variables
template_vars = {
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "session_date": "2025-08-21",
    "session_time": "2:00 PM",
    "session_type": "Follow-up",
    "therapist_name": "Dr. Smith",
    "meeting_url": "https://meet.example.com/123",
    "reschedule_url": "https://cockpit.example.com/reschedule/123"
}
```

### Template Categories

- **Session Management**: Reminders, confirmations, reschedules
- **Client Onboarding**: Welcome, setup instructions, first session
- **Follow-up**: Post-session surveys, progress updates
- **Administrative**: Billing, policy updates, system maintenance
- **Emergency**: Urgent notifications, cancellations

## 🚀 CLI Commands

### Communication CLI

```bash
# Send test email
python blc.py comms email send --to test@example.com --template welcome

# Check delivery status
python blc.py comms status --tracking-id abc123

# View analytics
python blc.py comms analytics --client-id client123

# Manage templates
python blc.py comms template list
python blc.py comms template create --name new_template
python blc.py comms template test --name session_reminder
```

## 📈 Best Practices

### Message Timing
- **Emails**: 24-48 hours before sessions
- **SMS**: 1-2 hours before sessions
- **Push**: 15-30 minutes before sessions
- **Teams**: Real-time for urgent matters

### Content Guidelines
- Keep messages concise and actionable
- Include clear call-to-action buttons
- Provide opt-out options
- Use personalization when possible
- Test templates before deployment

### Compliance
- Respect opt-out preferences
- Include required legal disclaimers
- Log all communications for audit
- Follow HIPAA guidelines for healthcare
- Implement rate limiting to prevent spam

---

*This guide covers the communication automation system. For implementation details, see the API reference and development setup guides.*
