from unittest.mock import AsyncMock, patch

import pytest
from conftest import TestingSessionLocal

from app.db.session import AsyncSession
from app.tasks.notifications import notify_pending_suggestions_async


@pytest.mark.asyncio(loop_scope="session")
@patch("app.tasks.notifications.send_slack_notification", new_callable=AsyncMock)
async def test_no_pending_suggestions(
    mock_slack, db_session: AsyncSession, test_suggestion_approved
):
    """
    If there are no pending suggestions, Slack should NOT be called.
    """
    await notify_pending_suggestions_async(TestingSessionLocal)

    # Confirm Slack was never called
    mock_slack.assert_not_awaited()


@pytest.mark.asyncio(loop_scope="session")
@patch("app.tasks.notifications.send_slack_notification", new_callable=AsyncMock)
async def test_some_pending_suggestions(
    mock_slack, db_session: AsyncSession, test_suggestion_pending
):
    """
    If there's at least 1 suggestion with status=PENDING,
    we should call Slack with the correct message.
    """
    await notify_pending_suggestions_async(TestingSessionLocal)

    # Confirm Slack was called exactly once
    mock_slack.assert_awaited_once()
    # Check the first call's args
    args, kwargs = mock_slack.call_args
    # We expect something like "🔔 1 pending suggestions need review."
    assert "1 pending suggestions" in args[0], f"Got Slack message: {args[0]}"
