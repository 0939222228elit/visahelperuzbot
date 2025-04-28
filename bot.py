# bot.py

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
    user_data[message.chat.id] = {"answers": [], "current_q": 0}
    await message.answer(text_templates.start_text)
    await asyncio.sleep(1)
    await message.answer(questions.QUESTIONS[0])

@dp.message()
async def handle_answers(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        await message.answer("Нажмите /start для начала.")
        return

    data = user_data[chat_id]
    data["answers"].append(message.text)
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await message.answer(questions.QUESTIONS[data["current_q"]])
    else:
        result, show_alternative = evaluate_answers(data["answers"])
        await message.answer(result)

        if show_alternative:
            kb = [[types.KeyboardButton(text="Хочу узнать подробнее")]]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(text_templates.low_chances_text, reply_markup=keyboard)
        else:
            await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")

        user_data.pop(chat_id)

@dp.message(lambda message: message.text == "Хочу узнать подробнее")
async def alternative_path(message: types.Message):
    kb = [[types.KeyboardButton(text="Узнать страну")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text_templates.alternative_info_text, reply_markup=keyboard)

@dp.message(lambda message: message.text == "Узнать страну")
async def reveal_country(message: types.Message):
    await message.answer(text_templates.ukraine_info_text)

def evaluate_answers(answers):
    score = 0

    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    profession_keywords = ["строитель", "сварщик", "инженер", "электрик", "плиточник", "штукатур", "маляр"]
    if any(prof in answers[1].lower() for prof in profession_keywords):
        score += 1

    if answers[2].lower() in ["да", "имеется", "есть"]:
        score += 1
    if answers[3].lower() in ["да", "имеется", "есть"]:
        score += 1
    if "b1" in answers[4].lower():
        score += 1
    if answers[5].lower() in ["да", "имеется", "есть"]:
        score += 1

    percentage = int((score / 6) * 100)

    if percentage >= 80:
        return (text_templates.high_chances_text, False)
    else:
        return (text_templates.low_chances_text, True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
