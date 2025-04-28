import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, ADMIN_ID

# Вопросы для опроса
questions = [
    "Сколько вам лет?",
    "Какая у вас профессия? (например, строитель, сварщик, инженер и т.д.)",
    "Есть ли у вас диплом или профильное образование?",
    "Есть ли у вас опыт работы по специальности минимум 2 года?",
    "Какой у вас уровень немецкого языка? (например, B1, A2, нет)",
    "Есть ли у вас приглашение на работу в Германию?"
]

# Состояние пользователя
user_data = {}

# Создание кнопок
yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ],
    resize_keyboard=True
)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.chat.id] = {"step": 0, "answers": []}
    await message.answer("Добро пожаловать!\n\nЭтот бот поможет вам проверить шансы на получение визы в Германию и узнать о новом проекте по официальному трудоустройству в Европу!")
    await message.answer(questions[0])

# Обработчик ответов
@dp.message()
async def handle_answer(message: types.Message):
    user = user_data.get(message.chat.id)

    if not user:
        await message.answer("Пожалуйста, нажмите /start чтобы начать заново.")
        return

    step = user["step"]
    user["answers"].append(message.text)
    step += 1

    if step < len(questions):
        user["step"] = step
        if step >= 2:  # Начиная с 3-го вопроса ставим кнопки "Да/Нет"
            await message.answer(questions[step], reply_markup=yes_no_keyboard)
        else:
            await message.answer(questions[step])
    else:
        await message.answer("Спасибо за ваши ответы! Ваша анкета передана на обработку.", reply_markup=types.ReplyKeyboardRemove())
        print(f"Новая анкета от {message.chat.id}: {user['answers']}")
        del user_data[message.chat.id]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
