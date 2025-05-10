import pytest
from aiogram import types
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch
from datetime import datetime


@pytest.mark.asyncio
async def test_start_handler():
    from src.handlers.start import cmd_start

    user = types.User(
        id=12345,
        is_bot=False,
        first_name="Test",
        username="test_user"
    )

    chat = types.Chat(
        id=67890,
        type="private"
    )

    message = types.Message(
        message_id=1,
        date=datetime.now(),
        chat=chat,
        from_user=user,
        text="/start"
    )

    state = AsyncMock(spec=FSMContext)

    # 🧪 Перехватываем вызов answer
    with patch.object(types.Message, "answer", new_callable=AsyncMock) as mock_answer:
        await cmd_start(message, state)
        mock_answer.assert_called_once()