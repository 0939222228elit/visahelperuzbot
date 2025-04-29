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


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def start(message: types.Message, state: FSMContext):
    await message.answer(text_templates.start_text)
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

    await message.answer(result_text, reply_markup=generate_next_steps(is_high_chance))
    await bot.send_message(ADMIN_ID, f"Новая анкета от {message.from_user.id}: {list(data.values())}")
    await state.clear()


async def alternative_info(message: types.Message):
    await message.answer(text_templates.alternative_info_text)


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

    percentage = int((score / 6) * 100)
    return (
        text_templates.high_chance_text if percentage >= 70 else text_templates.low_chance_text,
        percentage >= 70
    )


def generate_next_steps(is_high_chance):
    if is_high_chance:
        return ReplyKeyboardRemove()
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Хочу узнать подробнее")]],
        resize_keyboard=True
    )


async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(process_age, Form.age)
    dp.message.register(process_profession, Form.profession)
    dp.message.register(process_education, Form.education)
    dp.message.register(process_experience, Form.experience)
    dp.message.register(process_language, Form.language)
    dp.message.register(process_invitation, Form.invitation)
    dp.message.register(alternative_info, F.text.lower() == "хочу узнать подробнее")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
