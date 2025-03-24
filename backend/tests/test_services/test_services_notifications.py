import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.notifications import send_slack_notification

URL = settings.SLACK_WEBHOOK_URL


@pytest.mark.asyncio(loop_scope="session")
@respx.mock
async def test_send_slack_notification_success():
    """
    Test the function with a real `httpx.AsyncClient`
    but mock Slack's endpoint so we don't make a real request.
    """

    # 1) check if the url is actually good.
    assert "hooks.slack.com" in URL, "Expected a Slack URL"

    # 2) Setup a fake Slack route that returns 200 OK.
    #    "hooks.slack.com" is in the function's check.
    slack_route = respx.post(URL).mock(return_value=Response(200, content=b"OK"))

    # 3) Call the real function—no big patches here
    result = await send_slack_notification("Test message")

    # 4) Assertions
    assert slack_route.called, "Expected Slack route to be called."
    assert result == "Notification sent successfully"
