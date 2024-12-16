# main.py

import logging
import asyncio
from aiogram import Bot, Dispatcher
import config
from handlers import common, city

async def main():
    API_TOKEN = config.token

    # Включаем логирование, чтобы видеть сообщения в консоли
    logging.basicConfig(level=logging.INFO)

    # Инициализация бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(city.router)
    dp.include_router(common.router)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())