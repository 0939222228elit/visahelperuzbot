import asyncio from aiogram import Bot, Dispatcher, F, types from aiogram.fsm.context import FSMContext from aiogram.fsm.state import State, StatesGroup from aiogram.filters import CommandStart from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from config import BOT_TOKEN, ADMIN_ID import text_templates import questions

FSM - Машина состояний

class Form(StatesGroup): age = State() profession = State() education = State() experience = State() language = State() invitation = State()

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

user_data = {}

@dp.message(CommandStart()) async def start(message: types.Message, state: FSMContext): await message.answer(text_templates.start_text) await message.answer(questions.QUESTIONS[0]) await state.set_state(Form.age)

@dp.message(Form.age) async def process_age(message: types.Message, state: FSMContext): await state.update_data(age=message.text) await message.answer(questions.QUESTIONS[1]) await state.set_state(Form.profession)

@dp.message(Form.profession) async def process_profession(message: types.Message, state: FSMContext): await state.update_data(profession=message.text) await message.answer(questions.QUESTIONS[2]) await state.set_state(Form.education)

@dp.message(Form.education) async def process_education(message: types.Message, state: FSMContext): await state.update_data(education=message.text) await message.answer(questions.QUESTIONS[3]) await state.set_state(Form.experience)

@dp.message(Form.experience) async def process_experience(message: types.Message, state: FSMContext): await state.update_data(experience=message.text) await message.answer(questions.QUESTIONS[4]) await state.set_state(Form.language)

@dp.message(Form.language) async def process_language(message: types.Message, state: FSMContext): await state.update_data(language=message.text) await message.answer(questions.QUESTIONS[5]) await state.set_state(Form.invitation)

@dp.message(Form.invitation) async def process_invitation(message: types.Message, state: FSMContext): await state.update_data(invitation=message.text) data = await state.get_data()

result_text, is_high_chance = evaluate_answers(data)

await message.answer(result_text, reply_markup=generate_next_steps(is_high_chance))

# Отправляем анкету админу
await bot.send_message(ADMIN_ID, f"Новая анкета от {message.from_user.id}: {list(data.values())}")

await state.clear()

Оценка ответов

def evaluate_answers(data): score = 0

# Возраст
try:
    age = int(data['age'])
    if 20 <= age <= 55:
        score += 1
except:
    pass

# Профессия
if data['profession'].lower() in questions.VALID_PROFESSIONS:
    score += 1

# Диплом
if data['education'].lower() == "да":
    score += 1

# Опыт
if data['experience'].lower() == "да":
    score += 1

# Язык
if data['language'].upper() == "B1":
    score += 1

# Приглашение
if data['invitation'].lower() == "да":
    score += 1

percentage = int((score / 6) * 100)

if percentage >= 70:
    return text_templates.high_chance_text, True
else:
    return text_templates.low_chance_text, False

Генерация кнопок

def generate_next_steps(is_high_chance): if is_high_chance: return types.ReplyKeyboardRemove() else: markup = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="Хочу узнать подробнее")] ], resize_keyboard=True ) return markup

@dp.message(F.text.lower() == "хочу узнать подробнее") async def alternative_info(message: types.Message): await message.answer(text_templates.alternative_info_text)

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

