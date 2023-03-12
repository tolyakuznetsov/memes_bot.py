import images
from config_reader import config
from aiogram import Bot, Dispatcher, executor, types
import logging
import keyboard as kb
import open_files as of
import images as img
import requests
import io


async def start_command_handler(message: types.Message):
    await message.reply(of.send_welcome_text(), reply_markup=kb.inline_kb1)


class TelegramBot:

    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)
        self.setup_handlers()

    def setup_handlers(self):
        self.dp.register_message_handler(start_command_handler, commands=['start'])
        self.dp.register_callback_query_handler(self.start_game_handler, lambda c: c.data == 'button_start_game')
        self.dp.register_callback_query_handler(self.rules_handler, lambda c: c.data == 'button_rules')
        self.dp.register_callback_query_handler(self.send_random_images_handler, lambda c: c.data == 'button_get_memes')
        self.dp.register_callback_query_handler(self.send_situation, lambda c: c.data == 'botton_get_situatoin')
        self.dp.register_callback_query_handler(self.send_image_to_chat,
                                                lambda query: query.data.startswith('image_path'))

    async def start_game_handler(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        await self.bot.send_message(chat_id, text='Начинаем! Ситуация:')
        await self.bot.send_message(chat_id, 'Нажми на кнопку ниже, чтобы получить мемы, а потом перейди в бота, '
                                             'чтобы разыграть карты', reply_markup=kb.inline_kb2)

    async def rules_handler(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        await self.bot.send_message(chat_id, of.send_rules())

    async def send_random_images_handler(self, callback_query: types.CallbackQuery):
        image_bytes_list = img.open_random_images(callback_query=callback_query)
        images.save_user_chat_to_db(callback_query.from_user.id, callback_query.message.chat.id)
        #chat_link = Bot.export_chat_invite_link(self, chat_id=callback_query.message.chat.id)
        #print(chat_link)
        dilimeter = of.dilimeter()
        await self.bot.send_photo(callback_query.from_user.id, photo=dilimeter)
        if image_bytes_list:
            for image_bytes in image_bytes_list:
                await self.bot.send_photo(callback_query.from_user.id, photo=image_bytes, reply_markup=kb.inline_kb3)
        else:
            await self.bot.send_message(callback_query.from_user.id, text='Все картинки уже были отправлены :(')

    async def send_image_to_chat(self, query: types.CallbackQuery):
        file_id = query.message.photo[-1].file_id
        file_info = await self.bot.get_file(file_id)
        image_url = f'https://api.telegram.org/file/bot{config.bot_token.get_secret_value()}/{file_info.file_path}'

        with requests.get(image_url, stream=True) as r:
            r.raise_for_status()
            with io.BytesIO(r.content) as image:
                await self.bot.send_photo(chat_id=images.get_mapp_user_chat(query.from_user.id), photo=image, caption='Карточка от ' + query.from_user.full_name)

    async def send_situation(self, callback_query: types.CallbackQuery):
        await self.bot.send_message(callback_query.message.chat.id, text=of.send_situation())



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # логгирование
    bot = TelegramBot(token=config.bot_token.get_secret_value())
    executor.start_polling(bot.dp, skip_updates=True)
