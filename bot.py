import asyncio from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton from config import BOT_TOKEN, ADMIN_ID import questions import text_templates

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

user_data = {}

@dp.message(CommandStart()) async def start_handler(message: types.Message): await message.answer(text_templates.start_text) user_data[message.chat.id] = {"answers": [], "current_q": 0} await message.answer(questions.QUESTIONS[0])

@dp.message() async def handle_answers(message: types.Message): chat_id = message.chat.id if chat_id not in user_data: await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.") return

data = user_data[chat_id]
data["answers"].append(message.text)
data["current_q"] += 1

if data["current_q"] < len(questions.QUESTIONS):
    await message.answer(questions.QUESTIONS[data["current_q"]])
else:
    result_text, need_offer = evaluate_answers(data["answers"])
    if need_offer:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Хочу узнать подробнее", callback_data="learn_more")]
        ])
        await message.answer(result_text, reply_markup=keyboard)
    else:
        await message.answer(result_text)
    await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")
    user_data.pop(chat_id)

@dp.callback_query() async def handle_callback(callback: types.CallbackQuery): if callback.data == "learn_more": await callback.message.answer(text_templates.ua_offer_text)

def evaluate_answers(answers): score = 0 try: age = int(answers[0]) if 20 <= age <= 45: score += 1 except: pass

profession = answers[1].lower()
suitable_professions = ["строитель", "сварщик", "инженер", "электрик", "медсестра", "повар"]
if profession in suitable_professions:
    score += 1

if answers[2].lower() in ["да", "имеется", "есть"]:
    score += 1

if answers[3].lower() in ["да", "имеется", "есть"]:
    score += 1

language = answers[4].lower()
if "b1" in language or "b2" in language:
    score += 1

if score >= 4:
    return (text_templates.high_chances_text, False)
else:
    return (text_templates.low_chances_text, True)

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

