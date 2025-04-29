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
    user_name = State()
    user_contact = State()
    user_comment = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# FSM Start
async def start(message: types.Message, state: FSMContext):
    await message.answer(text_templates.start_text)
    await asyncio.sleep(1.5)
    await message.answer(questions.QUESTIONS[0])
    await state.set_state(Form.age)

async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(questions.QUESTIONS[1])
    await state.set_state(Form.profession)

async def process_profession(message: types.Message, state: FSMContext):
    await state.update_data(profession=message.text)
    await message.answer(questions.QUESTIONS[2])
    await state.set_state(Form.education)

async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer(questions.QUESTIONS[3])
    await state.set_state(Form.experience)

async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer(questions.QUESTIONS[4])
    await state.set_state(Form.language)

async def process_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer(questions.QUESTIONS[5])
    await state.set_state(Form.invitation)

async def process_invitation(message: types.Message, state: FSMContext):
    await state.update_data(invitation=message.text)
    data = await state.get_data()
    result_text, is_high_chance = evaluate_answers(data)

    await asyncio.sleep(1.5)
    if is_high_chance:
        await message.answer(result_text)
        await bot.send_message(ADMIN_ID, f"Анкета от {message.from_user.username or message.from_user.id}: {list(data.values())}")
    else:
        await message.answer(text_templates.low_chance_intro, reply_markup=low_chance_keyboard())

    await state.clear()

# FSM Responses After Low Chance Path
async def handle_low_chance_choice(message: types.Message, state: FSMContext):
    text = message.text.lower()
    if "реальное решение" in text:
        await message.answer(text_templates.alternative_offer, reply_markup=alternative_offer_keyboard())
    elif "почему я не подхожу" in text:
        await message.answer(text_templates.rejection_reasons, reply_markup=back_to_start_keyboard())
    elif "назад" in text:
        await message.answer(text_templates.low_chance_intro, reply_markup=low_chance_keyboard())
    elif "узнать больше про украину" in text:
        await message.answer(text_templates.ukraine_details, reply_markup=final_cta_keyboard())
    elif "связаться с координатором" in text:
        await message.answer("Пожалуйста, укажите ваше имя:")
        await state.set_state(Form.user_name)
    elif "оставить заявку" in text:
        await message.answer("Введите ваш номер телефона или email для связи:")
        await state.set_state(Form.user_contact)

async def collect_user_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Спасибо! Теперь введите номер телефона или email:")
    await state.set_state(Form.user_contact)

async def collect_user_contact(message: types.Message, state: FSMContext):
    await state.update_data(user_contact=message.text)
    await message.answer("Последний шаг: добавьте короткий комментарий или вопрос (или напишите 'нет'):")
    await state.set_state(Form.user_comment)

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
    await message.answer("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время ✅")
    await state.clear()

# Support Functions
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

def low_chance_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔘 Хочу реальное решение")],
            [KeyboardButton(text="🔘 Почему я не подхожу?")],
        ],
        resize_keyboard=True
    )

def back_to_start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔘 Назад")]], resize_keyboard=True
    )

def alternative_offer_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔘 Узнать больше про Украину")],
            [KeyboardButton(text="🔘 Связаться с координатором")],
        ],
        resize_keyboard=True
    )

def final_cta_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔘 Связаться с координатором")],
            [KeyboardButton(text="🔘 Оставить заявку")],
            [KeyboardButton(text="🔘 Назад")],
        ],
        resize_keyboard=True
    )

# Register Handlers
dp.message.register(start, CommandStart())
dp.message.register(process_age, Form.age)
dp.message.register(process_profession, Form.profession)
dp.message.register(process_education, Form.education)
dp.message.register(process_experience, Form.experience)
dp.message.register(process_language, Form.language)
dp.message.register(process_invitation, Form.invitation)
dp.message.register(handle_low_chance_choice, F.text.lower().contains("реальное решение") | F.text.lower().contains("почему") | F.text.lower().contains("назад") | F.text.lower().contains("украину") | F.text.lower().contains("связаться") | F.text.lower().contains("заявку"))
dp.message.register(collect_user_name, Form.user_name)
dp.message.register(collect_user_contact, Form.user_contact)
dp.message.register(collect_user_comment, Form.user_comment)

# Main
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
