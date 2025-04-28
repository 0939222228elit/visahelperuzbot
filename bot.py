bot.py

import asyncio from aiogram import Bot, Dispatcher, types, F from aiogram.filters import CommandStart from config import BOT_TOKEN, ADMIN_ID import questions import text_templates

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

Память для пользователей

user_states = {}

@dp.message(CommandStart()) async def start_command(message: types.Message): user_states[message.chat.id] = {"current_step": 0, "answers": []} await message.answer(text_templates.start_text) await message.answer(questions.QUESTIONS[0])

@dp.message(F.text) async def process_answer(message: types.Message): user_id = message.chat.id if user_id not in user_states: await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.") return

state = user_states[user_id]
state["answers"].append(message.text)
state["current_step"] += 1

if state["current_step"] < len(questions.QUESTIONS):
    next_question = questions.QUESTIONS[state["current_step"]]
    await message.answer(next_question)
else:
    result_text = evaluate(state["answers"])
    await message.answer(result_text)
    await bot.send_message(ADMIN_ID, f"Новая анкета от {user_id}: {state['answers']}")
    user_states.pop(user_id)

def evaluate(answers): # Оценка ответов score = 0 try: age = int(answers[0]) if 20 <= age <= 50: score += 1 except ValueError: pass

profession = answers[1].lower()
if profession in ["строитель", "сварщик", "инженер", "электрик"]:
    score += 1

diploma = answers[2].lower()
if diploma in ["да", "есть"]:
    score += 1

experience = answers[3].lower()
if experience in ["да", "есть"]:
    score += 1

german_level = answers[4].lower()
if german_level == "b1":
    score += 1

invitation = answers[5].lower()
if invitation in ["да", "есть"]:
    score += 1

if score >= 5:
    return text_templates.high_chances_text
else:
    return text_templates.low_chances_text

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

