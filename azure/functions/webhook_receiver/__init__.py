import azure.functions as func
import logging
import json
import asyncio
import os
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from azure.dynamics_message_processor import dynamics_message_processor
from azure.messaging import MessagingFactory

async def main(req: func.HttpRequest, action: str) -> func.HttpResponse:
    """Handle webhook requests for various actions"""
    
    logging.info(f'Webhook received for action: {action}')
    
    try:
        # Get request body
        body = req.get_json()
        
        if action == "process_dynamics_messages":
            # Process Dynamics messages
            result = await dynamics_message_processor.process_dynamics_messages()
            
            return func.HttpResponse(
                json.dumps({
                    "status": "success",
                    "action": action,
                    "result": result
                }),
                mimetype="application/json"
            )
            
        elif action == "send_message":
            # Send a single message
            messaging_config = {
                'graph': {
                    'tenant_id': os.environ.get('AZURE_TENANT_ID'),
                    'client_id': os.environ.get('AZURE_CLIENT_ID'),
                    'client_secret': os.environ.get('AZURE_CLIENT_SECRET')
                },
                'respond': {
                    'api_key': os.environ.get('RESPOND_API_KEY'),
                    'workspace_id': os.environ.get('RESPOND_WORKSPACE_ID'),
                    'base_url': os.environ.get('RESPOND_BASE_URL', 'https://api.respond.io')
                }
            }
            
            messaging_factory = MessagingFactory(messaging_config)
            result = await messaging_factory.send_message(body)
            
            return func.HttpResponse(
                json.dumps({
                    "status": "success" if result.success else "failed",
                    "action": action,
                    "result": {
                        "success": result.success,
                        "provider": result.provider,
                        "external_id": result.external_id,
                        "error_message": result.error_message
                    }
                }),
                mimetype="application/json"
            )
            
        else:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "message": f"Unknown action: {action}"
                }),
                status_code=400,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f'Webhook processing failed: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )

# For local testing
if __name__ == "__main__":
    # Mock request for testing
    class MockRequest:
        def get_json(self):
            return {"test": "data"}
    
    asyncio.run(main(MockRequest(), "process_dynamics_messages"))
