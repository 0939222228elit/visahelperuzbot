import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID
import text_templates
import questions

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним ответы пользователей
user_states = {}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(text_templates.start_text)
    user_states[message.chat.id] = {"answers": [], "current_question": 0}
    await bot.send_message(message.chat.id, questions.QUESTIONS[0])

@dp.message()
async def answer_handler(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        await message.answer("Пожалуйста, нажмите /start чтобы начать заново.")
        return

    user_data = user_states[chat_id]
    user_data["answers"].append(message.text)
    user_data["current_question"] += 1

    if user_data["current_question"] < len(questions.QUESTIONS):
        await bot.send_message(chat_id, questions.QUESTIONS[user_data["current_question"]])
    else:
        result = evaluate(user_data["answers"])
        await message.answer(result)
        await bot.send_message(ADMIN_ID, f"Новая анкета:\n{user_data['answers']}")
        user_states.pop(chat_id)

def evaluate(answers):
    score = 0
    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    for answer in answers[1:]:
        if answer.lower() in ["да", "имеется", "есть"]:
            score += 1

    percentage = (score / 5) * 100

    if percentage >= 80:
        return text_templates.high_chances_text
    else:
        return text_templates.low_chances_text

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
