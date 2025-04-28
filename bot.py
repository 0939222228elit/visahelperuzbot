import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Берем токен и ID из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

questions = [
    "Сколько вам лет?",
    "Какая у вас профессия? (например, строитель, сварщик, инженер и т.д.)",
    "Есть ли у вас диплом или профильное образование?",
    "Есть ли у вас опыт работы по специальности минимум 2 года?",
    "Какой у вас уровень немецкого языка? (B1, A2, нет)",
    "Есть ли у вас приглашение на работу в Германию?"
]

user_data = {}

# Клавиатуры
yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="B1"), KeyboardButton(text="A2"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать!\n\n"
        "Этот бот поможет вам проверить шансы на получение визы в Германию "
        "и узнать о новом проекте по официальному трудоустройству в Европу!",
        reply_markup=types.ReplyKeyboardRemove()
    )
    user_data[message.chat.id] = {"answers": [], "current_q": 0}
    await ask_question(message.chat.id)

async def ask_question(chat_id):
    current_q = user_data[chat_id]["current_q"]
    
    if current_q >= len(questions):
        await evaluate(chat_id)
        return

    markup = None
    if current_q in [2, 3, 5]:  # вопросы с Да/Нет
        markup = yes_no_keyboard
    elif current_q == 4:  # вопрос про язык
        markup = lang_keyboard

    await bot.send_message(chat_id, questions[current_q], reply_markup=markup)

@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
        return

    user_data[chat_id]["answers"].append(message.text)
    user_data[chat_id]["current_q"] += 1
    await ask_question(chat_id)

async def evaluate(chat_id):
    answers = user_data[chat_id]["answers"]

    try:
        age = int(answers[0])
    except ValueError:
        age = 0

    profession = answers[1].lower()
    diploma = answers[2].lower()
    experience = answers[3].lower()
    language = answers[4].lower()
    invitation = answers[5].lower()

    good_professions = ["строитель", "сварщик", "инженер", "электрик", "плиточник", "маляр", "штукатур"]
    passed = True

    if not (20 <= age <= 55):
        passed = False
    if profession not in good_professions:
        passed = False
    if diploma != "да":
        passed = False
    if experience != "да":
        passed = False
    if language != "b1":
        passed = False

    if passed and invitation == "да":
        await bot.send_message(chat_id, 
            "Поздравляем! У вас высокие шансы получить визу в Германию!\n\n"
            "Что делать дальше:\n"
            "- Найдите вакансию на сайте [arbeitsagentur.de](https://www.arbeitsagentur.de)\n"
            "- Получите официальное приглашение.\n"
            "- Запишитесь на визу в консульство Германии."
        )
    else:
        await bot.send_message(chat_id, 
            "К сожалению, ваши шансы на получение визы в Германию сейчас невысокие.\n\n"
            "НО! Есть отличная альтернатива через специальную европейскую программу!\n"
            "Хотите узнать как за 3-5 месяцев получить ВНЖ и легально работать в Европе?\n\n"
            "Напишите 👉 Хочу узнать подробнее"
        )
    
    await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {answers}")
    user_data.pop(chat_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
