import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import BOT_TOKEN, ADMIN_ID
import questions
import text_templates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_answer = State()

user_data = {}

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(text_templates.start_text)
    user_data[message.chat.id] = {"answers": [], "current_q": 0}
    await bot.send_message(message.chat.id, questions.QUESTIONS[0])
    await state.set_state(Form.waiting_for_answer)

@dp.message(Form.waiting_for_answer)
async def handle_answer(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    data = user_data.get(chat_id)

    if not data:
        await message.answer("Нажмите /start для начала опроса.")
        return

    data["answers"].append(message.text)
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await bot.send_message(chat_id, questions.QUESTIONS[data["current_q"]])
    else:
        result = evaluate_answers(data["answers"])
        await bot.send_message(chat_id, result)
        await bot.send_message(ADMIN_ID, f"Новая анкета: {data['answers']}")
        user_data.pop(chat_id)
        await state.clear()

def evaluate_answers(answers):
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

    percentage = int((score / 5) * 100)

    if percentage >= 80:
        return text_templates.high_chances_text
    else:
        return text_templates.low_chances_text

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
