import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID
import questions
import text_templates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def start_handler(message: types.Message):
    await message.answer(text_templates.start_message)
    await ask_questions(message.chat.id)

user_data = {}

async def ask_questions(chat_id):
    user_data[chat_id] = {"answers": [], "current_q": 0}
    await bot.send_message(chat_id, questions.QUESTIONS[0])

@dp.message()
async def handle_answers(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    data = user_data[chat_id]
    current_q = data["current_q"]

    data["answers"].append(message.text)
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await bot.send_message(chat_id, questions.QUESTIONS[data["current_q"]])
    else:
        result = evaluate_answers(data["answers"])
        await bot.send_message(chat_id, result)
        await bot.send_message(ADMIN_ID, f"Новая заявка: {data['answers']}")
        user_data.pop(chat_id)

def evaluate_answers(answers):
    score = 0

    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    if answers[1].lower() in ["да", "имеется"]:
        score += 1
    if answers[2].lower() in ["да", "имеется"]:
        score += 1
    if answers[3].lower() in ["да", "имеется"]:
        score += 1
    if answers[4].lower() in ["да", "есть"]:
        score += 1

    percentage = int((score / 5) * 100)

    if percentage >= 80:
        return text_templates.high_chance_text
    else:
        return text_templates.low_chance_text

async def main():
    dp.message.register(start_handler, CommandStart())
    dp.message.register(handle_answers)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
