"""
Life Cockpit Safety Guardrails

Enforces safe defaults and approval workflows for all operations.
"""

import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
from enum import Enum
import structlog

logger = structlog.get_logger()

class Classification(Enum):
    """Operation classification levels"""
    PERSONAL = "personal"
    BUSINESS = "business"
    CLINICAL = "clinical"

class GuardrailManager:
    """Manages safety guardrails for all operations"""
    
    def __init__(self):
        self.dry_run_default = os.getenv("BLC_DRY_RUN_DEFAULT", "true").lower() == "true"
        self.require_approval = os.getenv("BLC_REQUIRE_APPROVAL", "true").lower() == "true"
        self.classification_enforcement = os.getenv("BLC_CLASSIFICATION_ENFORCEMENT", "true").lower() == "true"
        self.local_sandbox = os.getenv("BLC_LOCAL_SANDBOX", "false").lower() == "true"
        
        # Track active run IDs
        self.active_runs: Dict[str, Dict[str, Any]] = {}
        
        logger.info("GuardrailManager initialized", 
                   dry_run_default=self.dry_run_default,
                   require_approval=self.require_approval,
                   classification_enforcement=self.classification_enforcement,
                   local_sandbox=self.local_sandbox)
    
    def create_run_id(self, operation: str, classification: Classification) -> str:
        """Create a unique run ID for tracking operations"""
        run_id = str(uuid.uuid4())
        
        self.active_runs[run_id] = {
            'operation': operation,
            'classification': classification.value,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'created',
            'dry_run': self.dry_run_default,
            'approved': False
        }
        
        logger.info("Created run ID", run_id=run_id, operation=operation, classification=classification.value)
        return run_id
    
    def approve_run(self, run_id: str) -> bool:
        """Approve a run for execution"""
        if run_id not in self.active_runs:
            logger.error("Run ID not found", run_id=run_id)
            return False
        
        self.active_runs[run_id]['approved'] = True
        self.active_runs[run_id]['status'] = 'approved'
        self.active_runs[run_id]['approved_at'] = datetime.utcnow().isoformat()
        
        logger.info("Run approved", run_id=run_id)
        return True
    
    def is_approved(self, run_id: str) -> bool:
        """Check if a run is approved"""
        if not self.require_approval:
            return True
        
        if run_id not in self.active_runs:
            return False
        
        return self.active_runs[run_id].get('approved', False)
    
    def is_dry_run(self, run_id: str) -> bool:
        """Check if a run is in dry-run mode"""
        if run_id not in self.active_runs:
            return self.dry_run_default
        
        return self.active_runs[run_id].get('dry_run', self.dry_run_default)
    
    def complete_run(self, run_id: str, success: bool = True, result: Optional[Dict[str, Any]] = None):
        """Mark a run as completed"""
        if run_id not in self.active_runs:
            logger.error("Run ID not found for completion", run_id=run_id)
            return
        
        self.active_runs[run_id]['status'] = 'completed' if success else 'failed'
        self.active_runs[run_id]['completed_at'] = datetime.utcnow().isoformat()
        self.active_runs[run_id]['success'] = success
        self.active_runs[run_id]['result'] = result
        
        logger.info("Run completed", run_id=run_id, success=success)
    
    def get_run_info(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a run"""
        return self.active_runs.get(run_id)
    
    def list_runs(self, status: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List all runs, optionally filtered by status"""
        if status:
            return {run_id: run_info for run_id, run_info in self.active_runs.items() 
                   if run_info.get('status') == status}
        return self.active_runs.copy()

# Global guardrail manager instance
guardrail_manager = GuardrailManager()

def safe_operation(classification: Classification, operation_name: str = None):
    """
    Decorator for safe operations with guardrails
    
    Usage:
        @safe_operation(Classification.BUSINESS, "client-report-generate")
        async def generate_client_report(client_id: str, run_id: str):
            # Operation logic here
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract run_id from kwargs or create one
            run_id = kwargs.get('run_id')
            if not run_id:
                run_id = guardrail_manager.create_run_id(
                    operation_name or func.__name__, 
                    classification
                )
                kwargs['run_id'] = run_id
            
            # Check if operation is approved
            if not guardrail_manager.is_approved(run_id):
                logger.warning("Operation not approved", 
                             run_id=run_id, 
                             operation=operation_name or func.__name__)
                return {
                    'success': False,
                    'error': 'Operation not approved. Use --approve flag.',
                    'run_id': run_id,
                    'dry_run': guardrail_manager.is_dry_run(run_id)
                }
            
            # Check if in dry-run mode
            is_dry_run = guardrail_manager.is_dry_run(run_id)
            
            try:
                logger.info("Executing operation", 
                           run_id=run_id, 
                           operation=operation_name or func.__name__,
                           dry_run=is_dry_run,
                           classification=classification.value)
                
                # Only add dry_run if it's not already in kwargs
                if 'dry_run' not in kwargs:
                    kwargs['dry_run'] = is_dry_run
                elif is_dry_run and not kwargs.get('dry_run'):
                    # If guardrails say dry_run but caller says not, enforce dry_run
                    kwargs['dry_run'] = True
                
                # Execute the function with the appropriate dry_run setting
                result = await func(*args, **kwargs)
                guardrail_manager.complete_run(run_id, True, result)
                
                return {
                    'success': True,
                    'dry_run': kwargs.get('dry_run', is_dry_run),
                    'message': 'Operation executed in dry-run mode' if kwargs.get('dry_run') else 'Operation executed successfully',
                    'run_id': run_id,
                    'result': result
                }
                    
            except Exception as e:
                logger.error("Operation failed", 
                           run_id=run_id, 
                           operation=operation_name or func.__name__,
                           error=str(e))
                guardrail_manager.complete_run(run_id, False, {'error': str(e)})
                return {
                    'success': False,
                    'error': str(e),
                    'run_id': run_id,
                    'dry_run': is_dry_run
                }
        
        return wrapper
    return decorator

def require_approval(classification: Classification):
    """
    Decorator for operations that require explicit approval
    
    Usage:
        @require_approval(Classification.CLINICAL)
        async def update_client_record(client_id: str, data: dict, run_id: str):
            # Clinical operation requiring approval
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            run_id = kwargs.get('run_id')
            if not run_id:
                run_id = guardrail_manager.create_run_id(func.__name__, classification)
                kwargs['run_id'] = run_id
            
            # Always require approval for clinical operations
            if classification == Classification.CLINICAL:
                if not guardrail_manager.is_approved(run_id):
                    return {
                        'success': False,
                        'error': f'Clinical operation requires explicit approval. Use --approve --clinical flags.',
                        'run_id': run_id,
                        'classification': classification.value
                    }
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Utility functions for CLI integration
def create_run_id(operation: str, classification: Classification) -> str:
    """Create a run ID for CLI operations"""
    return guardrail_manager.create_run_id(operation, classification)

def approve_run(run_id: str) -> bool:
    """Approve a run from CLI"""
    return guardrail_manager.approve_run(run_id)

def get_run_status(run_id: str) -> Optional[Dict[str, Any]]:
    """Get run status for CLI display"""
    return guardrail_manager.get_run_info(run_id)

def list_runs(status: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """List runs for CLI display"""
    return guardrail_manager.list_runs(status)
