import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID
import questions
import text_templates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"answers": [], "current_q": 0}
    await message.answer(text_templates.start_text)
    await message.answer(questions.QUESTIONS[0])

@dp.message(F.text)
async def handle_answers(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
        return

    data = user_data[chat_id]

    # Сохраняем ответ
    data["answers"].append(message.text)

    # Переходим к следующему вопросу
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await message.answer(questions.QUESTIONS[data["current_q"]])
    else:
        # Все вопросы пройдены
        result = evaluate_answers(data["answers"])
        await message.answer(result)
        await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")
        user_data.pop(chat_id)  # очищаем пользователя

def evaluate_answers(answers):
    score = 0
    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    for answer in answers[1:]:
        if answer.lower() in ["да", "есть", "имеется"]:
            score += 1

    percentage = int((score / 5) * 100)

    if percentage >= 80:
        return text_templates.high_chances_text
    else:
        return text_templates.low_chances_text

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
