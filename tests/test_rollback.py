"""Tests for rollback utilities."""

import pytest
import tempfile
import json
from pathlib import Path
from utils.rollback import RollbackManager, get_rollback_manager


class TestRollbackManager:
    """Test RollbackManager functionality."""
    
    def test_init(self):
        """Test RollbackManager initialization."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = RollbackManager(temp_path)
            assert manager.storage_path == Path(temp_path)
            assert manager.rollback_points == {}
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_create_point(self):
        """Test creating a rollback point."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = RollbackManager(temp_path)
            
            point_id = manager.create_point(
                operation="test_operation",
                description="Test rollback point",
                data={"key": "value"}
            )
            
            assert point_id in manager.rollback_points
            assert manager.rollback_points[point_id]["operation"] == "test_operation"
            assert manager.rollback_points[point_id]["description"] == "Test rollback point"
            assert manager.rollback_points[point_id]["data"]["key"] == "value"
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_list_points(self):
        """Test listing rollback points."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = RollbackManager(temp_path)
            
            # Create some points
            manager.create_point("op1", "First operation", {"data": 1})
            manager.create_point("op2", "Second operation", {"data": 2})
            
            points = manager.list_points()
            assert len(points) == 2
            
            # Check that points contain expected data
            op1_found = any(p["operation"] == "op1" for p in points.values())
            op2_found = any(p["operation"] == "op2" for p in points.values())
            assert op1_found
            assert op2_found
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestRollbackManagerGlobal:
    """Test global rollback manager."""
    
    def test_get_rollback_manager(self):
        """Test getting global rollback manager."""
        manager1 = get_rollback_manager()
        manager2 = get_rollback_manager()
        
        # Should return the same instance
        assert manager1 is manager2
