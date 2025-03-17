import httpx
from app.core.config import settings
from typing import Optional


async def send_slack_notification(message: str) -> Optional[str]:
    """Send a notification to Slack via webhook, with additional checks."""

    # 1) Check if the URL is missing or the placeholder
    slack_url = settings.SLACK_WEBHOOK_URL
    if not slack_url or "hooks.slack.com" not in slack_url:
        return "Slack webhook URL is missing or invalid"

    try:
        # 2) Make the request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_url,
                json={"text": message},
                timeout=10,  # prevent hanging
            )

        # 3) Extra safety: check if we actually got a response
        if response is None:
            return "No response received from Slack"

        # Optionally, check if Slack returned an empty body
        if not response.content:
            return "Slack response was empty or had no content"

        # 4) Raise an HTTPStatusError on 4xx or 5xx
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        # Slack returned a non-2xx status
        return f"Failed to send Slack notification: {e.response.text}"

    except httpx.RequestError as e:
        # A network or request-level error occurred
        return f"Request error: {str(e)}"

    # 5) Otherwise, success
    return "Notification sent successfully"
