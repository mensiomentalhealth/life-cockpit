#!/usr/bin/env python3
"""
Message Dashboard Web Interface

Provides a web interface to:
- View scheduled messages queue
- Send messages manually
- View message logs
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.messaging import MessagingFactory
from utils.sandbox import get_sandbox_dataverse

logger = structlog.get_logger()

app = FastAPI(title="Message Dashboard", version="1.0.0")

# Initialize services
dataverse = get_sandbox_dataverse()

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

messaging_factory = MessagingFactory(messaging_config)

# Templates
templates = Jinja2Templates(directory="web/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    try:
        # Get scheduled messages
        messages = await get_scheduled_messages()
        
        # Get message logs
        logs = await get_message_logs()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "messages": messages,
            "logs": logs,
            "stats": {
                "pending": len([m for m in messages if m['status'] == 'revised']),
                "sent": len([m for m in messages if m['status'] == 'sent']),
                "failed": len([m for m in messages if m['status'] == 'failed'])
            }
        })
    except Exception as e:
        logger.error("Dashboard error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages")
async def get_messages():
    """API endpoint to get scheduled messages"""
    try:
        messages = await get_scheduled_messages()
        return {"messages": messages}
    except Exception as e:
        logger.error("Get messages error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send/{message_id}")
async def send_message(message_id: str):
    """API endpoint to send a specific message"""
    try:
        # Get the message
        message = await get_message_by_id(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if message['status'] != 'revised':
            raise HTTPException(status_code=400, detail="Message is not ready to send")
        
        # Send the message
        result = await messaging_factory.send_message(message)
        
        if result.success:
            # Log the message
            await log_message_sent(message, result)
            
            # Update message status
            await update_message_status(message_id, 'sent', result.external_id)
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "external_id": result.external_id,
                "provider": result.provider
            }
        else:
            # Mark as failed
            await update_message_status(message_id, 'failed', error_message=result.error_message)
            
            return {
                "success": False,
                "message": "Failed to send message",
                "error": result.error_message
            }
            
    except Exception as e:
        logger.error("Send message error", message_id=message_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-test-message")
async def create_test_message():
    """Create a test message for testing"""
    try:
        test_message = {
            'session_id': 'test-session',
            'client_id': 'test-client',
            'message_type': 'email',
            'recipient': 'test@example.com',
            'subject': 'Test Message from Dashboard',
            'body': 'This is a test message created via the dashboard API.',
            'send_time': datetime.utcnow().isoformat(),
            'status': 'revised'
        }
        
        await dataverse.create_record('scheduled_messages', test_message)
        
        return {
            "success": True,
            "message": "Test message created successfully",
            "message_id": test_message.get('id', 'new')
        }
        
    except Exception as e:
        logger.error("Failed to create test message", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-all")
async def send_all_pending():
    """API endpoint to send all pending messages"""
    try:
        # Get pending messages
        messages = await get_scheduled_messages()
        pending = [m for m in messages if m['status'] == 'revised']
        
        if not pending:
            return {"success": True, "message": "No pending messages to send"}
        
        results = []
        for message in pending:
            try:
                # Send the message
                result = await messaging_factory.send_message(message)
                
                if result.success:
                    # Log the message
                    await log_message_sent(message, result)
                    
                    # Update message status
                    await update_message_status(message['id'], 'sent', result.external_id)
                    
                    results.append({
                        "message_id": message['id'],
                        "success": True,
                        "external_id": result.external_id,
                        "provider": result.provider
                    })
                else:
                    # Mark as failed
                    await update_message_status(message['id'], 'failed', error_message=result.error_message)
                    
                    results.append({
                        "message_id": message['id'],
                        "success": False,
                        "error": result.error_message
                    })
                    
            except Exception as e:
                logger.error("Failed to send message", message_id=message['id'], error=str(e))
                await update_message_status(message['id'], 'failed', error_message=str(e))
                
                results.append({
                    "message_id": message['id'],
                    "success": False,
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])
        
        return {
            "success": True,
            "message": f"Processed {len(results)} messages: {success_count} sent, {failed_count} failed",
            "results": results
        }
        
    except Exception as e:
        logger.error("Send all messages error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def get_scheduled_messages() -> List[Dict[str, Any]]:
    """Get all scheduled messages"""
    try:
        messages = await dataverse.query_records(
            'scheduled_messages',
            orderby='send_time asc'
        )
        return messages
    except Exception as e:
        logger.error("Failed to get scheduled messages", error=str(e))
        return []

async def get_message_logs() -> List[Dict[str, Any]]:
    """Get message logs"""
    try:
        logs = await dataverse.query_records(
            'messages_log',
            orderby='sent_at desc',
            top=50
        )
        return logs
    except Exception as e:
        logger.error("Failed to get message logs", error=str(e))
        return []

async def get_message_by_id(message_id: str) -> Dict[str, Any]:
    """Get a specific message by ID"""
    try:
        message = await dataverse.get_record('scheduled_messages', message_id)
        return message
    except Exception as e:
        logger.error("Failed to get message", message_id=message_id, error=str(e))
        return None

async def log_message_sent(message: Dict[str, Any], result) -> None:
    """Log a sent message"""
    try:
        log_entry = {
            'message_id': message['id'],
            'message_type': message['message_type'],
            'recipient': message.get('recipient'),
            'subject': message.get('subject'),
            'body': message['body'],
            'status': 'sent',
            'sent_at': datetime.utcnow().isoformat(),
            'provider': result.provider,
            'message_id_external': result.external_id
        }
        
        await dataverse.create_record('messages_log', log_entry)
        logger.info("Logged message sent", message_id=message['id'])
        
    except Exception as e:
        logger.error("Failed to log message", message_id=message['id'], error=str(e))

async def update_message_status(message_id: str, status: str, external_id: str = None, error_message: str = None) -> None:
    """Update message status"""
    try:
        update_data = {
            'status': status,
            'processed_time': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if external_id:
            update_data['metadata'] = json.dumps({'external_id': external_id})
        
        if error_message:
            update_data['error_message'] = error_message
        
        await dataverse.update_record('scheduled_messages', message_id, update_data)
        logger.info("Updated message status", message_id=message_id, status=status)
        
    except Exception as e:
        logger.error("Failed to update message status", message_id=message_id, error=str(e))

if __name__ == "__main__":
    print("🚀 Starting Message Dashboard...")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
