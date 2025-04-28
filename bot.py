bot.py

import asyncio from aiogram import Bot, Dispatcher, F, types from aiogram.filters import CommandStart from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

Профессии, которые имеют высокий шанс

VALID_PROFESSIONS = ["строитель", "сварщик", "инженер", "электрик", "плиточник", "маляр", "штукатур", "бетонщик"]

user_data = {}

Клавиатуры

start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Начать опрос")]], resize_keyboard=True) yes_no_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")],[KeyboardButton(text="Нет")]], resize_keyboard=True) alternative_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Узнать альтернативу")]], resize_keyboard=True)

@dp.message(CommandStart()) async def cmd_start(message: types.Message): await message.answer( "Добро пожаловать!\n\nЭтот бот поможет вам проверить шансы на получение визы в Германию и узнать о новом проекте трудоустройства в Европу!", reply_markup=start_kb )

@dp.message(F.text.lower() == "начать опрос") async def start_survey(message: types.Message): user_data[message.chat.id] = {"answers": [], "step": 0} await message.answer("Сколько вам лет?", reply_markup=types.ReplyKeyboardRemove())

@dp.message() async def handle_survey(message: types.Message): chat_id = message.chat.id

if chat_id not in user_data:
    await message.answer("Пожалуйста, нажмите /start чтобы начать.", reply_markup=start_kb)
    return

step = user_data[chat_id]["step"]
text = message.text.strip()

if step == 0:
    if not text.isdigit():
        await message.answer("Введите возраст цифрами.")
        return
    user_data[chat_id]["age"] = int(text)
    user_data[chat_id]["step"] = 1
    await message.answer("Какая у вас профессия? (например, строитель, сварщик, инженер)")

elif step == 1:
    user_data[chat_id]["profession"] = text.lower()
    user_data[chat_id]["step"] = 2
    await message.answer("Есть ли у вас диплом или профильное образование?", reply_markup=yes_no_kb)

elif step == 2:
    user_data[chat_id]["diploma"] = text.lower()
    user_data[chat_id]["step"] = 3
    await message.answer("Есть ли у вас опыт работы по специальности минимум 2 года?", reply_markup=yes_no_kb)

elif step == 3:
    user_data[chat_id]["experience"] = text.lower()
    user_data[chat_id]["step"] = 4
    await message.answer("Какой у вас уровень немецкого языка? (например, B1, A2, нет)", reply_markup=types.ReplyKeyboardRemove())

elif step == 4:
    user_data[chat_id]["language"] = text.upper()
    user_data[chat_id]["step"] = 5
    await message.answer("Есть ли у вас приглашение на работу в Германию?", reply_markup=yes_no_kb)

elif step == 5:
    user_data[chat_id]["invitation"] = text.lower()
    await evaluate_answers(chat_id, message)
    user_data.pop(chat_id)

async def evaluate_answers(chat_id, message): data = user_data[chat_id] score = 0

if 20 <= data["age"] <= 55:
    score += 1

if data["profession"] in VALID_PROFESSIONS:
    score += 1

if data["diploma"] == "да":
    score += 1

if data["experience"] == "да":
    score += 1

if data["language"] in ["B1", "B2", "C1", "C2"]:
    score += 1

if data["invitation"] == "да":
    score += 1

# Высокие шансы — минимум 5 из 6 баллов
if score >= 5:
    await message.answer(
        "Поздравляем! Ваши шансы на получение визы в Германию высоки!\n\nЧто делать дальше:\n- Найдите вакансию через сайт arbeitsagentur.de\n- Подайте заявку.\n- Получите приглашение.\n- Запишитесь на визу через QuickCheck."
    )
else:
    await message.answer(
        "К сожалению, ваши шансы на получение визы в Германию сейчас невысокие.\n\nНО! Есть отличная альтернатива через специальную европейскую программу!\nХотите узнать, как за 3-5 месяцев получить ВНЖ и легально работать в Европе?",
        reply_markup=alternative_kb
    )

# Отправить администратору анкету
await bot.send_message(
    ADMIN_ID,
    f"Новая анкета:\nВозраст: {data['age']}\nПрофессия: {data['profession']}\nДиплом: {data['diploma']}\nОпыт: {data['experience']}\nЯзык: {data['language']}\nПриглашение: {data['invitation']}"
)

@dp.message(F.text.lower() == "узнать альтернативу") async def show_alternative(message: types.Message): await message.answer( "\u2705 Программа ""Европа+"":\n\n- Безвизовый переезд через Украину.\n- Работа на строительстве и производстве.\n- Бесплатное жилье.\n- Оформление ВНЖ за 3-5 месяцев.\n- После — работа в Германии с зарплатой от 3000 евро!\n\nКоличество мест ограничено. Стартовать можно очень быстро!\n\nХотите оставить заявку на участие? Пишите прямо сюда!" )

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

