from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# Кнопки начала
button_start_game = InlineKeyboardButton('Начать игру', callback_data='button_start_game')
button_rules = InlineKeyboardButton('Ознакомиться с правилами', callback_data='button_rules')
inline_kb1 = InlineKeyboardMarkup().add(button_start_game).add(button_rules)

# Кнопки для получения мемов
button_go_to_bot = InlineKeyboardButton(text="Перейти в бота", url="https://t.me/mem_haha_bot")
button_get_memes = InlineKeyboardButton('Получить мемы', callback_data='button_get_memes')
inline_kb2 = InlineKeyboardMarkup().add(button_get_memes).add(button_go_to_bot)

button_send_image_to_chat = InlineKeyboardButton("Отправить картинку в чат", callback_data="image_path:/path/to/image.jpg")
inline_kb3 = InlineKeyboardMarkup().add(button_send_image_to_chat)
