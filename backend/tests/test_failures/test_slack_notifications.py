import pytest
from unittest.mock import AsyncMock, patch
from app.services.notifications import send_slack_notification


@pytest.mark.asyncio
@patch("app.services.notifications.httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_send_slack_notification_failure(mock_post):
    """Test handling of Slack API failure when sending notifications."""
    mock_post.return_value.status_code = 500  # Simulating Slack failure

    with pytest.raises(Exception, match="Failed to send Slack notification"):
        await send_slack_notification("Test failure message")

    # Ensure the API was called once
    mock_post.assert_called_once()
