import pytest
from unittest.mock import MagicMock, patch
from mpclib.mac_manager import MacManager

@pytest.fixture
def manager():
    return MacManager()

def test_tag(manager):
    """
    Test tagging (storing MACs) for shares.
    """
    with patch('mpclib.mac_manager.macify') as mock_macify:
        mock_macify.return_value = "mac_shares_mock"
        shares = "shares_mock"
        manager.tag("test_id", shares)
        
        assert manager._macs["test_id"] == "mac_shares_mock"
        mock_macify.assert_called_once()

def test_verify_open_success(manager):
    """
    Test successful verification of opened values.
    """
    manager._macs["test_id"] = "stored_macs"
    with patch('mpclib.mac_manager.check_open') as mock_check:
        mock_check.return_value = True
        shares = "shares"
        opened = "opened"
        result = manager.verify_open("test_id", shares, opened)
        assert result is True
        mock_check.assert_called_with(opened, shares, "stored_macs", manager.ctx)

def test_verify_open_failure(manager):
    """
    Test failed verification of opened values.
    """
    manager._macs["test_id"] = "stored_macs"
    with patch('mpclib.mac_manager.check_open') as mock_check:
        mock_check.return_value = False
        assert manager.verify_open("test_id", "s", "o") is False

def test_verify_open_missing(manager):
    """
    Test verification with missing MACs.
    """
    with pytest.raises(KeyError):
        manager.verify_open("missing", "s", "o")
