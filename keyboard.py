from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,


class Buttons:
    def __init__(self):
        self.inline_kb_count_users = None
        self.inline_kb1 = None
        self.inline_kb2 = None
        self.inline_kb3 = None
        self.inline_kb4 = None
        self.inline_kb5 = None
        self.inline_kb6 = None

        self.create_inline_kb1()
        self.create_inline_kb2()
        self.create_inline_kb3()
        self.create_inline_kb5()
        self.create_inline_kb6()
        self.create_inline_kb_count_users()

    def create_inline_kb1(self):
        button_start_game = InlineKeyboardButton('Начать игру', callback_data='button_start_game')
        button_rules = InlineKeyboardButton('Ознакомиться с правилами', callback_data='button_rules')
        self.inline_kb1 = InlineKeyboardMarkup().add(button_start_game).add(button_rules)

    def create_inline_kb_count_users(self):
        button_count_users = InlineKeyboardButton('Укажите количество игроков', callback_data='button_count_users')
        self.inline_kb_count_users = InlineKeyboardMarkup().add(button_count_users)

    def create_inline_kb_pick_hero(self):
        button_to_game = InlineKeyboardButton('Выбрать персонажа', callback_data='button_nicknames')
        button_nicknames = InlineKeyboardButton('Выбрать персонажа', callback_data='button_nicknames')
        self.inline_kb_count_users = InlineKeyboardMarkup().add(button_nicknames).add(button_to_game)

    def create_inline_kb2(self):
        button_go_to_bot = InlineKeyboardButton(text="Перейти в бота", url="https://t.me/mem_haha_bot")
        button_get_memes = InlineKeyboardButton('Получить мемы', callback_data='button_get_memes')
        botton_get_situatoin = InlineKeyboardButton(text="Получить ситуацию", callback_data='botton_get_situatoin')
        self.inline_kb2 = InlineKeyboardMarkup().add(botton_get_situatoin).add(button_get_memes).add(button_go_to_bot)

    def create_inline_kb3(self):
        button_send_image_to_chat = InlineKeyboardButton("Отправить картинку в чат",
                                                         callback_data="image_path:/path/to/image.jpg")
        self.inline_kb3 = InlineKeyboardMarkup().add(button_send_image_to_chat)

    def create_inline_kb4(self, chat_link):
        button_chat_link = InlineKeyboardButton(text="Перейти в чат", url=chat_link)
        self.inline_kb4 = InlineKeyboardMarkup().add(button_chat_link)

    def create_inline_kb5(self):
        button_clean_db = InlineKeyboardButton(text="Закончить игру", callback_data='button_clean_db')
        self.inline_kb5 = InlineKeyboardMarkup().add(button_clean_db)

    def create_inline_kb6(self):
        button_description = InlineKeyboardButton(text="Описание", callback_data='button_description')
        self.inline_kb6 = InlineKeyboardMarkup().add(button_description)

    def create_inline_kb_pers(self):
        pass


buttons = Buttons()
inline_kb1 = buttons.inline_kb1
inline_kb2 = buttons.inline_kb2
inline_kb3 = buttons.inline_kb3
inline_kb4 = buttons.inline_kb4
inline_kb5 = buttons.inline_kb5
inline_kb6 = buttons.inline_kb6
inline_kb_count_users = buttons.inline_kb_count_users
