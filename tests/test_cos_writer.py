from unittest.mock import MagicMock, patch

import pytest

from cos_writer import write_order_json


@pytest.fixture
def mock_cos_env(monkeypatch):
    """Fixture to mock COS environment variables."""
    monkeypatch.setenv("COS_BUCKET", "test-bucket")
    monkeypatch.setenv("COS_API_KEY", "test-key")
    monkeypatch.setenv("COS_INSTANCE_CRN", "test-crn")
    monkeypatch.setenv("COS_ENDPOINT", "https://test.endpoint.com")


@patch("cos_writer._client")
def test_write_order_json(mock_client, mock_cos_env):
    """Test order is written to COS with correct key format."""
    mock_s3 = MagicMock()
    mock_client.return_value = mock_s3

    order = {"id": "o-123", "customer": "C-1", "total": 100.0}

    key = write_order_json(order)

    assert key.startswith("orders/dt=")
    assert "orderId=o-123.json" in key
    mock_s3.put_object.assert_called_once()
