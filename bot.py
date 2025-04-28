import asyncio from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart from config import BOT_TOKEN, ADMIN_ID import questions import text_templates

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

Храним информацию о пользователях

user_data = {}

@dp.message(CommandStart()) async def start_handler(message: types.Message): chat_id = message.chat.id user_data[chat_id] = {"answers": [], "current_q": 0} await message.answer(text_templates.start_text) await message.answer(questions.QUESTIONS[0])

@dp.message() async def handle_answers(message: types.Message): chat_id = message.chat.id

if chat_id not in user_data:
    await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
    return

data = user_data[chat_id]
answer = message.text.strip()
data["answers"].append(answer)
data["current_q"] += 1

if data["current_q"] < len(questions.QUESTIONS):
    await message.answer(questions.QUESTIONS[data["current_q"]])
else:
    # Завершение опроса и расчет шансов
    result_text, summary = evaluate_answers(data["answers"])
    await message.answer(result_text)
    await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {summary}")
    user_data.pop(chat_id)

Функция оценки анкетных данных

def evaluate_answers(answers): score = 0 summary = f"Ответы: {answers}"

try:
    age = int(answers[0])
    if 20 <= age <= 55:
        score += 1
except:
    pass

profession = answers[1].lower()
allowed_professions = ["строитель", "сварщик", "инженер", "электрик", "айтишник", "врач", "механик"]
if any(prof in profession for prof in allowed_professions):
    score += 1

diploma = answers[2].lower()
if diploma in ["да", "есть"]:
    score += 1

experience = answers[3].lower()
if experience in ["да", "есть"]:
    score += 1

german_level = answers[4].lower()
if "b1" in german_level:
    score += 1

invitation = answers[5].lower()
if invitation in ["да", "есть"]:
    score += 1

percentage = int((score / 6) * 100)

if percentage >= 80:
    return text_templates.high_chances_text, summary
else:
    return text_templates.low_chances_text, summary

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

