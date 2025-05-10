import pytest
from aiogram import types
from unittest.mock import AsyncMock, patch
from datetime import datetime


@pytest.fixture
def bot():
    return AsyncMock()


@pytest.fixture
def dp(bot):
    from aiogram import Dispatcher
    return Dispatcher(bot=bot)  # Используем именованный параметр


@pytest.mark.asyncio
async def test_start_handler(dp):
    from src.handlers.start import cmd_start
    from aiogram.fsm.context import FSMContext

    # Мокируем state
    mock_state = AsyncMock(spec=FSMContext)

    # Мокируем answer
    with patch('aiogram.types.message.Message.answer', new_callable=AsyncMock) as mock_answer:
        # Создаём сообщение
        message = types.Message(
            message_id=1,
            date=datetime.now(),
            chat=types.Chat(id=67890, type="private"),
            from_user=types.User(id=12345, is_bot=False, first_name="Test"),
            text="/start"
        )

        # Вызываем обработчик
        await cmd_start(message, mock_state)

        # Проверяем, что answer вызывался
        mock_answer.assert_called_once()

        # Проверяем, что set_state вызывался (если нужно)
        # mock_state.set_state.assert_called_once_with(...)
