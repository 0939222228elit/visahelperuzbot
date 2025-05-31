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
    country_ukraine = State()
    country_armenia = State()
    country_moldova = State()
    country_georgia = State()
    waiting_for_application = State()
    user_name = State()
    user_contact = State()
    user_comment = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def type_and_send(message: types.Message, text: str, delay: float = 1.5):
    await message.bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(delay)
    await message.answer(text)

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
        await type_and_send(message, text_templates.low_chance_intro)
        await message.answer("👇 Выберите страну, куда хотите поехать:", reply_markup=country_choice_keyboard())
        await state.set_state(AltStates.waiting_for_country)

async def choose_country(message: types.Message, state: FSMContext):
    country_text = message.text.lower()
    if "украина" in country_text:
        await type_and_send(message, text_templates.ukraine_text)
    elif "армения" in country_text:
        await type_and_send(message, text_templates.armenia_text)
    elif "молдова" in country_text:
        await type_and_send(message, text_templates.moldova_text)
    elif "грузия" in country_text:
        await type_and_send(message, text_templates.georgia_text)
    else:
        await message.answer("Пожалуйста, выберите страну из списка.")
        return

    await message.answer("✍️ Хотите подать заявку? Укажите ваше имя:")
    await state.set_state(AltStates.user_name)

async def collect_user_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("📞 Введите номер телефона или email:")
    await state.set_state(AltStates.user_contact)

async def collect_user_contact(message: types.Message, state: FSMContext):
    await state.update_data(user_contact=message.text)
    await message.answer("💬 Добавьте короткий комментарий или напишите 'нет':")
    await state.set_state(AltStates.user_comment)

async def collect_user_comment(message: types.Message, state: FSMContext):
    await state.update_data(user_comment=message.text)
    data = await state.get_data()
    summary = (
        f"📥 Новая заявка:\n"
        f"👤 Имя: {data.get('user_name')}\n"
        f"📞 Контакт: {data.get('user_contact')}\n"
        f"💬 Комментарий: {data.get('user_comment')}\n"
        f"🔗 Telegram: @{message.from_user.username or message.from_user.id}"
    )
    await bot.send_message(ADMIN_ID, summary)
    await type_and_send(message, text_templates.thank_you_text)
    await state.clear()

def evaluate_answers(data):
    score = 0
    try:
        age = int(data['age'])
        if 20 <= age <= 55:
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

def country_choice_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇦 Украина"), KeyboardButton(text="🇦🇲 Армения")],
            [KeyboardButton(text="🇲🇩 Молдова"), KeyboardButton(text="🇬🇪 Грузия")]
        ],
        resize_keyboard=True
    )

dp.message.register(start, CommandStart())
dp.message.register(process_age, Form.age)
dp.message.register(process_profession, Form.profession)
dp.message.register(process_education, Form.education)
dp.message.register(process_experience, Form.experience)
dp.message.register(process_language, Form.language)
dp.message.register(process_invitation, Form.invitation)
dp.message.register(choose_country, AltStates.waiting_for_country)
dp.message.register(collect_user_name, AltStates.user_name)
dp.message.register(collect_user_contact, AltStates.user_contact)
dp.message.register(collect_user_comment, AltStates.user_comment)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
