import pytest
from unittest.mock import AsyncMock, patch
from app.tasks.notifications import notify_pending_suggestions
from app.services.notifications import send_slack_notification


@pytest.mark.asyncio
@patch("app.services.notifications.send_slack_notification", new_callable=AsyncMock)
async def test_notify_pending_suggestions(mock_send_notification):
    """Test that the notification task correctly triggers Slack notifications."""
    mock_send_notification.return_value = None  # Mocking as it doesn't return anything

    await notify_pending_suggestions()

    # Verify the mock was called
    mock_send_notification.assert_called()
