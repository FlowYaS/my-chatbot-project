# handlers/common.py:
from aiogram import Router, types, F
from aiogram.filters.command import Command
from keyboards.keyboards import kb1, kb2
from handlers.random_fox import fox
from random import randint

router = Router()

# Хендлер на команду /start
@router.message(Command("start"))
@router.message(F.text.lower() == 'назад')
async def cmd_start(message: types.Message):
    name = message.chat.first_name
    await message.answer(f"Привет, {name}!", reply_markup=kb1)

# Хендлер на команду /stop
@router.message(Command("stop"))
@router.message(F.text.lower() == 'стоп')
@router.message(F.text.lower() == 'закрыть')
async def cmd_stop(message: types.Message):
    name = message.chat.first_name
    await message.answer(f"Пока, {name}!")

# Хендлер на команду /fox
@router.message(Command("fox"))
@router.message(Command("лиса"))
@router.message(F.text.lower() == 'покажи лису')
async def cmd_fox(message: types.Message):
    name = message.chat.first_name
    img_fox= fox()
    await message.answer(f"Держи лису, {name}!")
    await message.answer_photo(photo=img_fox)

# для рассылки тем, кто уже общался с нами в боте
#    await bot.send_photo(message.from_user.id, photo=img_fox)

# Хендлер на сообщение "Случайное число"
@router.message(F.text.casefold() == "случайное число")
async def send_random(message: types.Message):
    number = randint(1, 10)
    await message.answer(f'{number}')

# Хендлер на сообщение
@router.message(F.text.lower())
async def cmd_echo(message: types.Message):
    msg_user = message.text.lower()
    name = message.chat.first_name
    if "привет" in msg_user:
        await message.answer(f"Привет, {name}!")
    elif "пока" in msg_user:
        await message.answer(f"До встречи, {name}!")
    elif "дартс" in msg_user:
        await message.answer_dice(emoji='🎯')
    elif "поиграем" in msg_user:
        await message.answer(f"Выбирай игру, {name}", reply_markup=kb2)
    else:
        await message.answer(f"{name}, я не понимаю написанное")

