import asyncio from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart from aiogram.fsm.context import FSMContext from aiogram.fsm.state import State, StatesGroup from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from config import BOT_TOKEN, ADMIN_ID import text_templates import questions

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

Создание машины состояний

class Form(StatesGroup): age = State() profession = State() diploma = State() experience = State() language = State() invitation = State() alternative = State()

user_data = {}

@dp.message(CommandStart()) async def start_handler(message: types.Message, state: FSMContext): await message.answer(text_templates.start_text) await state.set_state(Form.age) user_data[message.chat.id] = [] await message.answer(questions.QUESTIONS["age"])

@dp.message(Form.age) async def process_age(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text) await state.set_state(Form.profession) await message.answer(questions.QUESTIONS["profession"])

@dp.message(Form.profession) async def process_profession(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text) await state.set_state(Form.diploma) keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")],[KeyboardButton(text="Нет")]], resize_keyboard=True) await message.answer(questions.QUESTIONS["diploma"], reply_markup=keyboard)

@dp.message(Form.diploma) async def process_diploma(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text) await state.set_state(Form.experience) await message.answer(questions.QUESTIONS["experience"])

@dp.message(Form.experience) async def process_experience(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text) await state.set_state(Form.language) await message.answer(questions.QUESTIONS["language"])

@dp.message(Form.language) async def process_language(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text) await state.set_state(Form.invitation) await message.answer(questions.QUESTIONS["invitation"])

@dp.message(Form.invitation) async def process_invitation(message: types.Message, state: FSMContext): user_data[message.chat.id].append(message.text)

result_text = evaluate(user_data[message.chat.id])
await message.answer(result_text, reply_markup=types.ReplyKeyboardRemove())

if "узнать подробнее" in result_text.lower():
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Хочу узнать подробнее")]], resize_keyboard=True)
    await state.set_state(Form.alternative)
    await message.answer("Нажмите кнопку ниже, чтобы узнать детали.", reply_markup=keyboard)
else:
    await bot.send_message(ADMIN_ID, f"Новая анкета: {user_data[message.chat.id]}")
    await state.clear()
    user_data.pop(message.chat.id, None)

@dp.message(Form.alternative) async def alternative_info(message: types.Message, state: FSMContext): await message.answer(text_templates.ukraine_program_text) await bot.send_message(ADMIN_ID, f"Новая анкета (альтернативный интерес): {user_data[message.chat.id]}") await state.clear() user_data.pop(message.chat.id, None)

def evaluate(answers): score = 0 try: age = int(answers[0]) if 20 <= age <= 50: score += 1 except: pass if answers[1].lower() in ["строитель", "сварщик", "инженер", "электрик", "медсестра"]: score += 1 if answers[2].lower() == "да": score += 1 if answers[3].lower() == "да": score += 1 if answers[4].lower() in ["b1", "b2", "c1"]: score += 1 if answers[5].lower() == "да": score += 1

if score >= 5:
    return text_templates.high_chances_text
else:
    return text_templates.low_chances_text

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

