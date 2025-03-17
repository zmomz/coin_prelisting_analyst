import pytest
from unittest.mock import AsyncMock, patch
from app.services.notifications import send_slack_notification
import httpx


@pytest.mark.asyncio(loop_scope="session")
async def test_missing_webhook_url(monkeypatch):
    """If SLACK_WEBHOOK_URL is missing or placeholder, it should return an error."""
    # 1) Force the config to be empty or the placeholder
    from app.core.config import settings
    monkeypatch.setattr(settings, "SLACK_WEBHOOK_URL", None)  # or "your_slack_webhook_url_here"

    # 2) Call the function
    result = await send_slack_notification("Hello Slack")

    # 3) Check the return
    assert result == "Slack webhook URL is missing or invalid"


@pytest.mark.asyncio(loop_scope="session")
@patch("app.services.notifications.httpx.AsyncClient", autospec=True)
async def test_successful_notification(MockAsyncClient):
    """
    Mocks a 200 OK from Slack and checks that we get "Notification sent successfully".
    """
    # 1) Prepare a mock response with 200
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.content = b"OK"
    mock_response.raise_for_status.return_value = None  # No error

    # 2) The async context manager "async with httpx.AsyncClient()" yields our mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    MockAsyncClient.return_value = mock_client_instance

    # 3) Force the config to have a valid Slack URL
    from app.core.config import settings
    original_url = settings.SLACK_WEBHOOK_URL
    settings.SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/REAL_WEBHOOK_URL"

    # 4) Call the function
    result = await send_slack_notification("Hello Slack")

    # 5) Restore original URL (cleanup)
    settings.SLACK_WEBHOOK_URL = original_url

    # 6) Assertions
    assert result == "Notification sent successfully"
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
@patch("app.services.notifications.httpx.AsyncClient", autospec=True)
async def test_failed_notification(MockAsyncClient):
    """
    Mocks a 500 error response from Slack, ensuring we return
    'Failed to send Slack notification: ...'.
    """
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.content = b"Something went wrong"
    # Ensure response.raise_for_status() raises HTTPStatusError
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Slack returned 500",
        request=httpx.Request("POST", "https://fake-slack-url"),
        response=httpx.Response(status_code=500, content=b"Something went wrong")
    )

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    MockAsyncClient.return_value = mock_client_instance

    from app.core.config import settings
    original_url = settings.SLACK_WEBHOOK_URL
    settings.SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/REAL_WEBHOOK_URL"

    result = await send_slack_notification("Slack test")
    settings.SLACK_WEBHOOK_URL = original_url

    assert "Failed to send Slack notification:" in result
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
@patch("app.services.notifications.httpx.AsyncClient", autospec=True)
async def test_no_content_response(MockAsyncClient):
    """
    If Slack responds with empty content, we return "Slack response was empty or had no content".
    """
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.content = b""
    mock_response.raise_for_status.return_value = None  # No status error

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    MockAsyncClient.return_value = mock_client_instance

    from app.core.config import settings
    original_url = settings.SLACK_WEBHOOK_URL
    settings.SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/REAL_WEBHOOK_URL"

    result = await send_slack_notification("Slack test")
    settings.SLACK_WEBHOOK_URL = original_url

    assert result == "Slack response was empty or had no content"
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
@patch("app.services.notifications.httpx.AsyncClient", autospec=True)
async def test_request_error(MockAsyncClient):
    """
    If a network error or timeout occurs, we return "Request error: ...".
    """
    mock_client_instance = AsyncMock()
    # Simulate any request-level error (e.g. timeout, DNS fail) by raising RequestError
    mock_client_instance.post.side_effect = httpx.RequestError("Network fail", request=httpx.Request("POST", ""))
    mock_client_instance.__aenter__.return_value = mock_client_instance
    MockAsyncClient.return_value = mock_client_instance

    from app.core.config import settings
    original_url = settings.SLACK_WEBHOOK_URL
    settings.SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/REAL_WEBHOOK_URL"

    result = await send_slack_notification("Slack test")
    settings.SLACK_WEBHOOK_URL = original_url

    assert "Request error:" in result
    mock_client_instance.post.assert_called_once()
