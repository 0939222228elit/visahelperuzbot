# bot.py

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from text_templates import *
from questions import questions

API_TOKEN = '6739363328:AAEqJpApA4b3DLSf1AnPgw2-mWNHgHCeEpg'
ADMIN_ID = 7406187939

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}

# Стартовая команда
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_data[message.chat.id] = {"step": 0, "score": 0}
    await message.answer(start_text)
    await send_question(message.chat.id)

# Функция отправки вопроса
async def send_question(chat_id):
    step = user_data[chat_id]["step"]
    if step < len(questions):
        question = questions[step]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for option in question["options"]:
            markup.add(KeyboardButton(option))
        await bot.send_message(chat_id, question["question"], reply_markup=markup)
    else:
        await show_results(chat_id)

# Обработчик всех сообщений
@dp.message()
async def handle_answer(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        await message.answer("Пожалуйста, нажмите /start чтобы начать.")
        return

    step = user_data[chat_id]["step"]
    if step < len(questions):
        try:
            selected = questions[step]["options"].index(message.text)
            user_data[chat_id]["score"] += questions[step]["weight"][selected]
            user_data[chat_id]["step"] += 1
            await send_question(chat_id)
        except ValueError:
            await message.answer("Пожалуйста, выберите вариант из предложенных кнопок.")
    else:
        await show_results(chat_id)

# Функция вывода результата
async def show_results(chat_id):
    score = user_data[chat_id]["score"]
    if score >= 9:
        await bot.send_message(chat_id, high_chances_text, disable_web_page_preview=True)
    else:
        await bot.send_message(chat_id, low_chances_text, disable_web_page_preview=True)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Узнать об альтернативном пути'))
    await bot.send_message(chat_id, ask_continue_text, reply_markup=markup)

# Альтернативный путь
@dp.message(lambda message: message.text == "Узнать об альтернативном пути")
async def send_alternative(message: types.Message):
    await message.answer(alternative_info_text, disable_web_page_preview=True)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
