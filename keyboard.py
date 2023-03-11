from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# Кнопки начала
button_start_game = InlineKeyboardButton('Начать игру', callback_data='button_start_game')
button_rules = InlineKeyboardButton('Ознакомиться с правилами', callback_data='button_rules')
inline_kb1 = InlineKeyboardMarkup().add(button_start_game).add(button_rules)

# Кнопки для получения мемов
button_get_memes = InlineKeyboardButton('Получить мемы', callback_data='button_get_memes')
inline_kb2 = InlineKeyboardMarkup().add(button_get_memes)
