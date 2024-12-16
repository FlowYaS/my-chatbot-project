import json
import random
import re
from aiogram import Router, F, types
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import os
from aiogram.enums import ParseMode
from keyboards.keyboards import kb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к файлу с городами
CITIES_FILE = os.path.join(os.path.dirname(__file__), "russian-cities.json")


def load_cities():
    """Загружает список городов из JSON-файла."""
    try:
        with open(CITIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка загрузки городов из файла: {e}")
        return []
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при загрузке городов: {e}")
        return []


def get_last_letter(city: str) -> str:
    """Возвращает последнюю букву города, игнорируя "ь", "ъ", "ы", "й" и небуквенные символы."""

    for char in reversed(city):
        if re.match(r'[а-яё]', char, re.IGNORECASE):
            if char.lower() in ['ь', 'ъ', 'ы', 'й']:
                continue
            return char.upper()
    return ''


class CityGame(StatesGroup):
    waiting_for_city = State()
    waiting_for_action = State()


router = Router()

cities_data = []
used_cities = set()


@router.message(F.text.casefold() == "города")
async def start_city_game(message: types.Message, state: FSMContext):
    """Начинает игру в города."""
    global cities_data, used_cities
    cities_data = load_cities()
    if not cities_data:
        await message.reply("Не удалось загрузить список городов. Попробуйте позже.")
        return

    used_cities.clear()
    await message.answer(
        "Давайте сыграем в игру 'Города'! Начните называть города. "
        "Если хотите сдаться, напишите 'сдаюсь'.\n\n"
        "**Примечание:** Список городов актуален для РФ по состоянию на 2020 год. "
        "Если название города заканчивается на буквы 'ь', 'ъ' , 'ы', 'й', "
        "можно пропускать, и следующий город нужно назвать на букву, которая находится перед ней."
        , parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(CityGame.waiting_for_city)


@router.message(CityGame.waiting_for_city)
async def play_city_game(message: types.Message, state: FSMContext):
    """Обрабатывает ввод пользователя во время игры."""
    global cities_data, used_cities
    user_city = message.text.strip()
    if user_city.lower() == "сдаюсь":
        await message.reply("Вы сдались. Игра окончена!", reply_markup=kb2)
        await state.clear()
        return

    if not user_city:
        await message.reply("Пожалуйста, введите название города.")
        return

    user_city_lower = user_city.lower()

    if user_city_lower in used_cities:
        await message.reply("Этот город уже был назван.")
        return

    city_data_from_file = next((city for city in cities_data if city['name'].lower() == user_city_lower), None)
    if not city_data_from_file:
        await message.reply("Такого города нет в списке.")
        return

    last_city_data = (await state.get_data()).get('last_city_data', None)
    if last_city_data:
        last_letter = get_last_letter(last_city_data['name'])
        if not user_city_lower.startswith(last_letter.lower()):
            await message.reply(f"Город должен начинаться с буквы '{last_letter}'.")
            return

    used_cities.add(user_city_lower)
    await state.update_data(last_city_data=city_data_from_file)

    bot_city = await get_bot_city(user_city_lower, cities_data, used_cities)
    if not bot_city:
        await message.reply("Я не могу назвать город. Вы победили!", reply_markup=kb2)
        await state.clear()
        return

    used_cities.add(bot_city['name'].lower())
    await state.update_data(last_city_data=bot_city)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Укажи регион", callback_data="region")],
            [types.InlineKeyboardButton(text="Мой город", callback_data="your_city")]
        ]
    )
    await message.reply(f"Хорошо, ваш город: {user_city}. Теперь мой ход: {bot_city['name']}.", reply_markup=keyboard)
    await state.set_state(CityGame.waiting_for_action)


@router.message(CityGame.waiting_for_action)
async def process_ignored_buttons(message: types.Message, state: FSMContext):
    """Обрабатывает сообщения пользователя, если он проигнорировал кнопки."""
    await play_city_game(message, state)


async def get_bot_city(user_city: str, cities_data: list, used_cities: set) -> dict or None:
    """Ищет подходящий город для ответа бота."""
    last_letter = get_last_letter(user_city)
    available_cities = [
        city for city in cities_data
        if city['name'].lower().startswith(last_letter.lower()) and city['name'].lower() not in used_cities
    ]
    if available_cities:
        return random.choice(available_cities)
    return None


@router.callback_query(CityGame.waiting_for_action)
async def cb_city_info(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатывает нажатия на кнопки во время игры."""
    global cities_data
    city_data = (await state.get_data()).get('last_city_data')
    if not city_data:
        return

    if callback_query.data == "region":
        region = city_data['subject']
        await callback_query.message.answer(f"Регион: {region}, теперь твой ход.")
        await state.set_state(CityGame.waiting_for_city)
    elif callback_query.data == "your_city":
        await message.answer(f"Теперь ваш ход, назовите город. Если хотите сдаться, напишите 'сдаюсь'.")
        await state.set_state(CityGame.waiting_for_city)
    await callback_query.answer()


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(router, skip_updates=True)