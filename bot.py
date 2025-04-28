import asyncio from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton from config import BOT_TOKEN, ADMIN_ID import questions import text_templates

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

user_data = {}

@dp.message(CommandStart()) async def start_handler(message: types.Message): await message.answer(text_templates.start_text) user_data[message.chat.id] = {"answers": [], "current_q": 0} await bot.send_message(message.chat.id, questions.QUESTIONS[0])

@dp.message() async def handle_answers(message: types.Message): chat_id = message.chat.id if chat_id not in user_data: await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.") return

data = user_data[chat_id]
data["answers"].append(message.text)
data["current_q"] += 1

if data["current_q"] < len(questions.QUESTIONS):
    await bot.send_message(chat_id, questions.QUESTIONS[data["current_q"]])
else:
    result_text = evaluate_answers(data["answers"])
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хочу узнать подробнее", callback_data="more_info")]
    ])
    await bot.send_message(chat_id, result_text, reply_markup=markup)
    await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")
    user_data.pop(chat_id)

@dp.callback_query() async def process_callback(callback_query: types.CallbackQuery): if callback_query.data == "more_info": await callback_query.message.answer(text_templates.more_info_text)

def evaluate_answers(answers): score = 0 try: age = int(answers[0]) if 22 <= age <= 50: score += 1 except: pass

profession = answers[1].lower()
if profession in ["строитель", "сварщик", "инженер", "электрик", "водитель", "механик"]:
    score += 1

diploma = answers[2].lower()
if diploma in ["да", "есть"]:
    score += 1

experience = answers[3].lower()
if experience in ["да", "есть"]:
    score += 1

language = answers[4].lower()
if language in ["b1", "b2", "c1"]:
    score += 1

invitation = answers[5].lower()
if invitation in ["да", "есть"]:
    score += 1

percentage = int((score / 6) * 100)

if percentage >= 70:
    return text_templates.high_chances_text
else:
    return text_templates.low_chances_text

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

