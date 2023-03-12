from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton


class Buttons:
    def __init__(self):
        self.inline_kb1 = None
        self.inline_kb2 = None
        self.inline_kb3 = None

        self.create_inline_kb1()
        self.create_inline_kb2()
        self.create_inline_kb3()

    def create_inline_kb1(self):
        button_start_game = InlineKeyboardButton('Начать игру', callback_data='button_start_game')
        button_rules = InlineKeyboardButton('Ознакомиться с правилами', callback_data='button_rules')
        self.inline_kb1 = InlineKeyboardMarkup().add(button_start_game).add(button_rules)

    def create_inline_kb2(self):
        button_go_to_bot = InlineKeyboardButton(text="Перейти в бота", url="https://t.me/mem_haha_bot")
        button_get_memes = InlineKeyboardButton('Получить мемы', callback_data='button_get_memes')
        self.inline_kb2 = InlineKeyboardMarkup().add(button_get_memes).add(button_go_to_bot)

    def create_inline_kb3(self):
        button_send_image_to_chat = InlineKeyboardButton("Отправить картинку в чат",
                                                         callback_data="image_path:/path/to/image.jpg")
        self.inline_kb3 = InlineKeyboardMarkup().add(button_send_image_to_chat)


buttons = Buttons()
inline_kb1 = buttons.inline_kb1
inline_kb2 = buttons.inline_kb2
inline_kb3 = buttons.inline_kb3
