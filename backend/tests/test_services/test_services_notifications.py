import pytest
from app.services.notifications import send_slack_notification
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
@patch("app.services.notifications.httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_send_slack_notification(mock_post):
    """Test sending a Slack notification."""
    mock_post.return_value.status_code = 200

    await send_slack_notification("Test message")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"] == {"text": "Test message"}
