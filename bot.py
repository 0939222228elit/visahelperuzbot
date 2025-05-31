# visa_bot/bot.py

import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import BOT_TOKEN, ADMIN_ID
import text_templates
import questions

class Form(StatesGroup):
    age = State()
    profession = State()
    education = State()
    experience = State()
    language = State()
    invitation = State()

class AltStates(StatesGroup):
    waiting_for_country = State()
    user_name = State()
    user_contact = State()
    user_comment = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def type_and_send(message: types.Message, text: str, delay: float = 1.5):
    await message.bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(delay)
    await message.answer(text, parse_mode="Markdown")

async def start(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"📥 Новый пользователь: @{message.from_user.username or message.from_user.id}")
    await type_and_send(message, text_templates.start_text)
    await type_and_send(message, questions.QUESTIONS[0])
    await state.set_state(Form.age)

async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await type_and_send(message, questions.QUESTIONS[1])
    await state.set_state(Form.profession)

async def process_profession(message: types.Message, state: FSMContext):
    await state.update_data(profession=message.text)
    await type_and_send(message, questions.QUESTIONS[2])
    await state.set_state(Form.education)

async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await type_and_send(message, questions.QUESTIONS[3])
    await state.set_state(Form.experience)

async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await type_and_send(message, questions.QUESTIONS[4])
    await state.set_state(Form.language)

async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await type_and_send(message, questions.QUESTIONS[5])
    await state.set_state(Form.invitation)

async def process_invitation(message: types.Message, state: FSMContext):
    await state.update_data(invitation=message.text)
    data = await state.get_data()
    result_text, is_high_chance = evaluate_answers(data)

    if is_high_chance:
        await type_and_send(message, result_text)
        await bot.send_message(ADMIN_ID, f"Анкета от {message.from_user.username or message.from_user.id}: {list(data.values())}")
        await state.clear()
    else:
        await type_and_send(message, text_templates.low_chance_detailed)
        await type_and_send(message, text_templates.country_intro)
        await message.answer("👇 Выберите страну, куда хотите поехать:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🇺🇦 Украина"), KeyboardButton(text="🇲🇩 Молдова")],
                     [KeyboardButton(text="🇦🇲 Армения"), KeyboardButton(text="🇬🇪 Грузия")]],
            resize_keyboard=True
        ))
        await state.set_state(AltStates.waiting_for_country)

async def choose_country(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current != AltStates.waiting_for_country.state:
        return

    country = message.text.lower().strip().replace("\\", "")

    if "украина" in country:
        await type_and_send(message, text_templates.ukraine_text)
    elif "армения" in country:
        await type_and_send(message, text_templates.armenia_text)
    elif "молдова" in country:
        await type_and_send(message, text_templates.moldova_text)
    elif "грузия" in country:
        await type_and_send(message, text_templates.georgia_text)
    else:
        await message.answer("Пожалуйста, выберите страну из предложенного списка ⬇️")
        return

    await message.answer("✍️ Пожалуйста, введите ваше имя:")
    await state.set_state(AltStates.user_name)

# Не забудь зарегистрировать choose_country в маршрутах: 
# dp.message.register(choose_country, AltStates.waiting_for_country)
