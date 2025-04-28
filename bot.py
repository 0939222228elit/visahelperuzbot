import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID
import questions
import text_templates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(text_templates.start_text)
    user_data[message.chat.id] = {"answers": [], "current_q": 0}
    await message.answer(questions.QUESTIONS[0])

@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
        return

    data = user_data[chat_id]
    data["answers"].append(message.text)
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await message.answer(questions.QUESTIONS[data["current_q"]])
    else:
        result = evaluate_answers(data["answers"])
        await message.answer(result)
        await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")
        user_data.pop(chat_id)

def evaluate_answers(answers):
    score = 0
    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    if "строитель" in answers[1].lower() or "сварщик" in answers[1].lower() or "инженер" in answers[1].lower():
        score += 1

    if answers[2].lower() == "да":
        score += 1

    if answers[3].lower() == "да":
        score += 1

    if "b1" in answers[4].lower():
        score += 1

    if score >= 4:
        return text_templates.high_chances_text
    else:
        return text_templates.low_chances_text

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
