import httpx
from app.core.config import settings


async def send_slack_notification(message: str):
    """Send a notification to Slack via webhook."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SLACK_WEBHOOK_URL,
            json={"text": message},
        )

        if response.status_code != 200:
            raise Exception(f"Failed to send Slack notification: {response.text}")
