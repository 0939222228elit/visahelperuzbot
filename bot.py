import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, ADMIN_ID
import text_templates
import questions

# Стандартные состояния анкеты
class Form(StatesGroup):
    age = State()
    profession = State()
    education = State()
    experience = State()
    language = State()
    invitation = State()

# Состояния альтернативной воронки
class AltStates(StatesGroup):
    waiting_for_alternative = State()
    waiting_for_program_info = State()
    waiting_for_start_process = State()
    waiting_for_application = State()
    user_name = State()
    user_contact = State()
    user_comment = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"📥 Новый пользователь: @{message.from_user.username or message.from_user.id}")
    await message.answer(text_templates.start_text)
    await asyncio.sleep(1.5)
    await message.answer(questions.QUESTIONS[0])
    await state.set_state(Form.age)

# Анкета
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(questions.QUESTIONS[1])
    await state.set_state(Form.profession)

@dp.message(Form.profession)
async def process_profession(message: types.Message, state: FSMContext):
    await state.update_data(profession=message.text)
    await message.answer(questions.QUESTIONS[2])
    await state.set_state(Form.education)

@dp.message(Form.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer(questions.QUESTIONS[3])
    await state.set_state(Form.experience)

@dp.message(Form.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer(questions.QUESTIONS[4])
    await state.set_state(Form.language)

@dp.message(Form.language)
async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer(questions.QUESTIONS[5])
    await state.set_state(Form.invitation)

@dp.message(Form.invitation)
async def process_invitation(message: types.Message, state: FSMContext):
    await state.update_data(invitation=message.text)
    data = await state.get_data()
    result_text, is_high_chance = evaluate_answers(data)
    await asyncio.sleep(1.5)
    if is_high_chance:
        await message.answer(result_text)
        await bot.send_message(ADMIN_ID, f"Анкета от {message.from_user.username or message.from_user.id}: {list(data.values())}")
        await state.clear()
    else:
        await message.answer(text_templates.low_chance_intro, reply_markup=alt_entry_kb())
        await state.set_state(AltStates.waiting_for_alternative)

# Альтернативная воронка
@dp.message(AltStates.waiting_for_alternative)
async def alt_alternative(message: types.Message, state: FSMContext):
    await message.answer(text_templates.alternative_warning, reply_markup=alt_program_kb())
    await state.set_state(AltStates.waiting_for_program_info)

@dp.message(AltStates.waiting_for_program_info)
async def alt_program_info(message: types.Message, state: FSMContext):
    await message.answer(text_templates.alternative_program, reply_markup=alt_start_kb())
    await state.set_state(AltStates.waiting_for_start_process)

@dp.message(AltStates.waiting_for_start_process)
async def alt_start_process(message: types.Message, state: FSMContext):
    await message.answer(text_templates.alternative_steps, reply_markup=alt_application_kb())
    await state.set_state(AltStates.waiting_for_application)

@dp.message(AltStates.waiting_for_application)
async def alt_application(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, укажите ваше имя:")
    await state.set_state(AltStates.user_name)

# Заявка
@dp.message(AltStates.user_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Спасибо! Теперь введите номер телефона или email:")
    await state.set_state(AltStates.user_contact)

@dp.message(AltStates.user_contact)
async def get_contact(message: types.Message, state: FSMContext):
    await state.update_data(user_contact=message.text)
    await message.answer("Последний шаг: добавьте короткий комментарий или напишите 'нет':")
    await state.set_state(AltStates.user_comment)

@dp.message(AltStates.user_comment)
async def get_comment(message: types.Message, state: FSMContext):
    await state.update_data(user_comment=message.text)
    data = await state.get_data()
    msg = (f"📥 Новая заявка:\n"
           f"Имя: {data.get('user_name')}\n"
           f"Контакт: {data.get('user_contact')}\n"
           f"Комментарий: {data.get('user_comment')}\n"
           f"Telegram: @{message.from_user.username or message.from_user.id}")
    await bot.send_message(ADMIN_ID, msg)
    await message.answer(text_templates.thank_you_text)
    await state.clear()

# Клавиатуры
def alt_entry_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 Узнать альтернативу")]], resize_keyboard=True)

def alt_program_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📋 Подробнее о программе")]], resize_keyboard=True)

def alt_start_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 Хочу начать оформление")]], resize_keyboard=True)

def alt_application_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✍️ Оставить заявку")]], resize_keyboard=True)

# Поддержка

def evaluate_answers(data):
    score = 0
    try:
        if 20 <= int(data['age']) <= 55:
            score += 1
    except:
        pass
    if data['profession'].lower() in questions.VALID_PROFESSIONS:
        score += 1
    if data['education'].lower() == "да":
        score += 1
    if data['experience'].lower() == "да":
        score += 1
    if data['language'].strip().upper() == "B1":
        score += 1
    if data['invitation'].lower() == "да":
        score += 1
    return text_templates.high_chance_text, (score / 6) * 100 >= 70

# Main
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
