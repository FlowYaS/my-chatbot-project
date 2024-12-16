# keyboards/keyboards.py

from aiogram import types

# Кнопки
button_start = types.KeyboardButton(text='/start')
button_random = types.KeyboardButton(text='Случайное число')
button_darts = types.KeyboardButton(text='Дартс')
button_fox = types.KeyboardButton(text='Покажи лису')
button_close = types.KeyboardButton(text='Закрыть')
button_back = types.KeyboardButton(text='Назад')
button_play = types.KeyboardButton(text='Поиграем')
button_cities = types.KeyboardButton(text='Города')

keyboard1 = [
    [button_start, button_play, button_close],
]

keyboard2 = [
    [button_random, button_darts, button_fox],
    [button_cities, button_back],
]

kb1 = types.ReplyKeyboardMarkup(keyboard=keyboard1, resize_keyboard=True)
kb2 = types.ReplyKeyboardMarkup(keyboard=keyboard2, resize_keyboard=True)
