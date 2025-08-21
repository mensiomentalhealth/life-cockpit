"""Rollback utilities for Life Cockpit."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class RollbackManager:
    """Basic rollback manager for critical operations."""
    
    def __init__(self, storage_path: str = "rollback_points.json"):
        self.storage_path = Path(storage_path)
        self.rollback_points: Dict[str, Dict[str, Any]] = {}
        self._load_points()
    
    def _load_points(self):
        """Load rollback points from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self.rollback_points = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load rollback points: {e}")
    
    def _save_points(self):
        """Save rollback points to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.rollback_points, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save rollback points: {e}")
    
    def create_point(self, operation: str, description: str, data: Dict[str, Any]) -> str:
        """Create a rollback point."""
        point_id = f"{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.rollback_points[point_id] = {
            'operation': operation,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self._save_points()
        logger.info(f"Created rollback point: {point_id}")
        return point_id
    
    def list_points(self) -> Dict[str, Dict[str, Any]]:
        """List all rollback points."""
        return self.rollback_points


# Global instance
_rollback_manager = None


def get_rollback_manager() -> RollbackManager:
    """Get global rollback manager."""
    global _rollback_manager
    if _rollback_manager is None:
        _rollback_manager = RollbackManager()
    return _rollback_manager
