           bot.py

import asyncio from aiogram import Bot, Dispatcher, F, types from aiogram.filters import CommandStart from aiogram.fsm.context import FSMContext from aiogram.fsm.state import State, StatesGroup from config import BOT_TOKEN, ADMIN_ID import text_templates

FSM States

class Form(StatesGroup): age = State() profession = State() diploma = State() experience = State() language = State() invitation = State()

Init

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

Start command

@dp.message(CommandStart()) async def start(message: types.Message, state: FSMContext): await message.answer(text_templates.start_text) await message.answer("Сколько вам лет?") await state.set_state(Form.age)

Age

@dp.message(Form.age) async def process_age(message: types.Message, state: FSMContext): await state.update_data(age=message.text) await message.answer("Какая у вас профессия? (например, строитель, сварщик, инженер)") await state.set_state(Form.profession)

Profession

@dp.message(Form.profession) async def process_profession(message: types.Message, state: FSMContext): await state.update_data(profession=message.text) await message.answer("Есть ли у вас диплом или профильное образование? (Да/Нет)") await state.set_state(Form.diploma)

Diploma

@dp.message(Form.diploma) async def process_diploma(message: types.Message, state: FSMContext): await state.update_data(diploma=message.text) await message.answer("Есть ли у вас опыт работы по специальности минимум 2 года? (Да/Нет)") await state.set_state(Form.experience)

Experience

@dp.message(Form.experience) async def process_experience(message: types.Message, state: FSMContext): await state.update_data(experience=message.text) await message.answer("Какой у вас уровень немецкого языка? (например, B1, A2, нет)") await state.set_state(Form.language)

Language

@dp.message(Form.language) async def process_language(message: types.Message, state: FSMContext): await state.update_data(language=message.text) await message.answer("Есть ли у вас приглашение на работу в Германию? (Да/Нет)") await state.set_state(Form.invitation)

Invitation and Final Result

@dp.message(Form.invitation) async def process_invitation(message: types.Message, state: FSMContext): await state.update_data(invitation=message.text) data = await state.get_data()

# Scoring logic
score = 0
try:
    age = int(data['age'])
    if 20 <= age <= 55:
        score += 1
except ValueError:
    pass

allowed_professions = ["строитель", "сварщик", "инженер", "электрик", "повар", "механик", "водитель", "маляр", "каменщик", "монтажник"]
if data['profession'].lower() in allowed_professions:
    score += 1

if data['diploma'].lower() == "да":
    score += 1
if data['experience'].lower() == "да":
    score += 1
if data['language'].lower() == "b1":
    score += 1
if data['invitation'].lower() == "да":
    score += 1

percentage = int((score / 6) * 100)

# Send results
if percentage >= 70:
    await message.answer(text_templates.high_chances_text)
else:
    await message.answer(text_templates.low_chances_text, reply_markup=text_templates.more_info_keyboard)

# Notify admin
await bot.send_message(ADMIN_ID, f"Новая анкета от {message.chat.id}: {data}")

await state.clear()

Alternative handler

@dp.message(F.text == "Хочу узнать подробнее") async def send_alternative_info(message: types.Message): await message.answer(text_templates.alternative_info_text)

Main

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

 
