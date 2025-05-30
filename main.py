import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from src.handlers import start, teacher, parent, behavior, admin  # 🔹 добавили behavior

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(parent.router)
dp.include_router(teacher.router)
dp.include_router(admin.router)
dp.include_router(behavior.router)  # 🔹 подключили behavior

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

