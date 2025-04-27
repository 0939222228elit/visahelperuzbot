from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Бот успешно запущен.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
