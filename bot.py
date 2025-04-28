import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_ID
import questions
import text_templates

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"answers": [], "current_q": 0}
    await message.answer(text_templates.start_text)
    await bot.send_message(chat_id, questions.QUESTIONS[0])

@dp.message()
async def handle_user_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip().lower()

    if chat_id not in user_data:
        if "хочу узнать подробнее" in text:
            await message.answer(
                "Отлично! Объясняем:\n\n"
                "- Вы можете без визы приехать в Украину.\n"
                "- Работа в строительстве или на производстве.\n"
                "- Бесплатное жилье предоставляется сразу!\n"
                "- Оформление ВНЖ за 3-5 месяцев.\n"
                "- После получения ВНЖ — подача на визу в Европу.\n"
                "- Зарплаты в Украине от **800 до 2000 долларов**.\n"
                "- После визы — работа в Германии от **3000 евро**.\n\n"
                "**Это легальный проект, курируемый европейскими компаниями!**\n\n"
                "Хотите узнать этапы оформления? Напишите 👉 _Хочу участвовать_"
            )
        elif "хочу участвовать" in text:
            await message.answer(
                "Поздравляем!\n\n"
                "**Этапы регистрации:**\n"
                "1. Заполните анкету (ссылка будет отправлена).\n"
                "2. Получите консультацию.\n"
                "3. Быстрое оформление выезда!\n\n"
                "Количество мест ограничено!"
            )
        else:
            await message.answer("Пожалуйста, нажмите /start чтобы начать опрос.")
        return

    data = user_data[chat_id]
    current_q = data["current_q"]

    data["answers"].append(message.text)
    data["current_q"] += 1

    if data["current_q"] < len(questions.QUESTIONS):
        await bot.send_message(chat_id, questions.QUESTIONS[data["current_q"]])
    else:
        result = evaluate_answers(data["answers"])
        await bot.send_message(chat_id, result)
        await bot.send_message(ADMIN_ID, f"Новая анкета от {chat_id}: {data['answers']}")
        user_data.pop(chat_id)

def evaluate_answers(answers):
    score = 0

    try:
        age = int(answers[0])
        if 20 <= age <= 55:
            score += 1
    except:
        pass

    good_professions = ["строитель", "сварщик", "инженер", "электрик", "монтажник"]
    profession = answers[1].lower()
    if any(prof in profession for prof in good_professions):
        score += 1

    if answers[2].lower() == "да":
        score += 1
    if answers[3].lower() == "да":
        score += 1
    if answers[4].lower() == "b1":
        score += 1
    if answers[5].lower() == "да":
        score += 1

    if score >= 5:
        return text_templates.high_chances_text
    else:
        return text_templates.low_chances_text

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
