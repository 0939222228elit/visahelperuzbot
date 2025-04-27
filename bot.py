import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from config import BOT_TOKEN, ADMIN_ID
from questions import questions
from text_templates import *

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Хранилище для ответов пользователей
user_data = {}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {
        'step': 0,
        'answers': []
    }
    await message.answer(start_text)
    await asyncio.sleep(1)
    await ask_next_question(message.from_user.id)

async def ask_next_question(user_id):
    user = user_data.get(user_id)
    if user is None:
        return
    step = user['step']
    if step < len(questions):
        question_text = questions[step]["text"]
        await bot.send_message(user_id, question_text)
    else:
        await evaluate_user(user_id)

@dp.message_handler(lambda message: message.from_user.id in user_data)
async def handle_answers(message: types.Message):
    user = user_data[message.from_user.id]
    user['answers'].append(message.text)
    user['step'] += 1
    await ask_next_question(message.from_user.id)

async def evaluate_user(user_id):
    user = user_data.get(user_id)
    if not user:
        return
    
    answers = user['answers']
    
    # Логика оценки шансов
    score = 0

    language_level = answers[0].lower()
    work_experience = int(answers[1])
    diploma = answers[2].lower()
    profession = answers[3].lower()

    if language_level in ['b1', 'b2', 'c1', 'c2']:
        score += 40
    if work_experience >= 2:
        score += 30
    if diploma == 'да':
        score += 20
    if profession in ['айтишник', 'строитель', 'инженер', 'медик']:
        score += 10

    result_message = f"Ваши шансы на получение визы в Германию: {score}%\n\n"

    if score >= 80:
        result_message += success_text
    else:
        result_message += alternative_offer_text

    await bot.send_message(user_id, result_message)
    await bot.send_message(user_id, finish_text)
    
    # Удаляем данные пользователя после оценки
    del user_data[user_id]

# Старт бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
