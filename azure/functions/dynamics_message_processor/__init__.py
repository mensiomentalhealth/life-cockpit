import azure.functions as func
import logging
import asyncio
import os
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from azure.dynamics_message_processor import dynamics_message_processor

async def main(timer: func.TimerRequest) -> None:
    """Process Dynamics messages every 5 minutes"""
    
    logging.info('Dynamics Message Processor triggered')
    
    try:
        # Process messages
        result = await dynamics_message_processor.process_dynamics_messages()
        
        logging.info(f'Processing completed: {result["processed_count"]} messages, {result["success_count"]} successful')
        
    except Exception as e:
        logging.error(f'Dynamics message processing failed: {str(e)}')
        raise

# For local testing
if __name__ == "__main__":
    asyncio.run(main(None))
