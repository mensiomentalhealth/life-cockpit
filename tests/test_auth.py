"""Tests for authentication modules."""

import pytest
from unittest.mock import Mock, patch
from auth.graph import GraphAuthManager
from auth.dataverse import DataverseAuthManager


class TestGraphAuthManager:
    """Test GraphAuthManager functionality."""
    
    def test_init(self):
        """Test GraphAuthManager initialization."""
        manager = GraphAuthManager()
        assert manager._credential is None
        assert manager._client is None
    
    @patch('auth.graph.ClientSecretCredential')
    def test_create_credential(self, mock_credential):
        """Test credential creation."""
        manager = GraphAuthManager()
        mock_credential.return_value = Mock()
        
        credential = manager._create_credential()
        assert credential is not None
        mock_credential.assert_called_once()


class TestDataverseAuthManager:
    """Test DataverseAuthManager functionality."""
    
    def test_init(self):
        """Test DataverseAuthManager initialization."""
        manager = DataverseAuthManager()
        assert manager._credential is None
        assert manager._dataverse_url is None
    
    @patch('auth.dataverse.ClientSecretCredential')
    def test_create_credential(self, mock_credential):
        """Test credential creation."""
        manager = DataverseAuthManager()
        mock_credential.return_value = Mock()
        
        credential = manager._create_credential()
        assert credential is not None
        mock_credential.assert_called_once()
