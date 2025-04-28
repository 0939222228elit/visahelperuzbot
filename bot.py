/app/bot.py

import asyncio from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton from config import BOT_TOKEN, ADMIN_ID from questions import QUESTIONS from text_templates import WELCOME_TEXT, NO_CHANCE_TEXT, SUCCESS_TEXT

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

user_data = {}

@dp.message(CommandStart()) async def start_handler(message: types.Message): user_data[message.from_user.id] = [] await message.answer(WELCOME_TEXT) await asyncio.sleep(1) await message.answer(QUESTIONS[0])

@dp.message() async def handle_answers(message: types.Message): user_id = message.from_user.id

if user_id not in user_data:
    await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
    return

user_data[user_id].append(message.text.strip())

if len(user_data[user_id]) < len(QUESTIONS):
    await message.answer(QUESTIONS[len(user_data[user_id])])
else:
    await evaluate_profile(message, user_data[user_id])
    user_data.pop(user_id, None)

async def evaluate_profile(message: types.Message, answers): age = int(answers[0]) if answers[0].isdigit() else 0 profession = answers[1].lower() diploma = answers[2].lower() experience = answers[3].lower() german_level = answers[4].upper() invitation = answers[5].lower()

good_professions = ["строитель", "сварщик", "инженер", "электрик", "механик", "водитель"]

if (18 <= age <= 45 and
    profession in good_professions and
    diploma == "да" and
    experience == "да" and
    german_level in ["B1", "B2"] and
    invitation == "да"):
    await message.answer(SUCCESS_TEXT)
else:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать подробнее", callback_data="more_info")]
    ])
    await message.answer(NO_CHANCE_TEXT, reply_markup=keyboard)

@dp.callback_query() async def callback_handler(callback: types.CallbackQuery): if callback.data == "more_info": await callback.message.answer( "Новая программа "Украина + Европа": граждане Азии могут быстро пройти адаптацию, получить квалификацию в Украине и затем получить ВНЖ с возможностью переезда в Германию! Подробнее - свяжитесь с нашим менеджером." ) await bot.send_message(ADMIN_ID, f"Новая анкета от {callback.from_user.id}: Хочет узнать подробнее.") await callback.answer()

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

