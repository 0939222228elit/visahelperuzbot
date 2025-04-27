from aiogram import Bot, Dispatcher, types, executor

# Твой токен бота
TOKEN = '7485677471:AAHXNl3oDsVaE1Q0SvFT2eyuy0-1lpSWxDg'

# Создание объектов бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Хэндлер на команду /start
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, Roman! Я VisaHelperUzBot. Чем могу помочь?")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
