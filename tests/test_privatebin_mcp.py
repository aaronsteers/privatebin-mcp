"""Unit tests for the privatebin_mcp module."""

import os
from unittest.mock import patch

import pytest

from privatebin_mcp.server import (
    _get_default_passcode,
    _get_server_url,
)


class TestPrivateBinMCP:
    """Test cases for the PrivateBin MCP server."""

    @pytest.mark.unit
    def test_get_server_url_success(self):
        """Test getting server URL from environment."""
        with patch.dict(os.environ, {"PRIVATEBIN_SERVER_URL": "https://test.example.com"}):
            result = _get_server_url()
            assert result == "https://test.example.com"

    @pytest.mark.unit
    def test_get_server_url_missing(self):
        """Test error when server URL is missing."""
        with patch.dict(os.environ, {}, clear=True):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="PRIVATEBIN_SERVER_URL environment variable is required"):
                _get_server_url()

    @pytest.mark.unit
    def test_get_default_passcode_present(self):
        """Test getting default passcode when present."""
        with patch.dict(os.environ, {"PRIVATEBIN_DEFAULT_PASSCODE": "secret123"}):
            result = _get_default_passcode()
            assert result == "secret123"

    @pytest.mark.unit
    def test_get_default_passcode_missing(self):
        """Test getting default passcode when missing returns empty string."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_default_passcode()
            assert result == ""
