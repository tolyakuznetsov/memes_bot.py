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
    chat_id = message.chat.id
    if chat_id == 274921311:
        await message.reply('Привет! Я бот для игры в ..., добавь меня в чат, чтобы начать игру',
                            reply_markup=kb.inline_kb6)
    else:
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
        self.dp.register_callback_query_handler(self.delete_images_from_db, lambda c: c.data == 'button_clean_db')
        self.dp.register_callback_query_handler(self.send_description, lambda c: c.data == 'button_description')

    async def start_game_handler(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        await self.bot.send_message(chat_id, text='Начинаем! Ситуация:')
        await self.bot.send_message(chat_id, 'Нажми на кнопку ниже, чтобы получить мемы, а потом перейди в бота, '
                                             'чтобы разыграть карты', reply_markup=kb.inline_kb2)
        await self.bot.send_message(chat_id, 'Закончить игру', reply_markup=kb.inline_kb5)

    async def send_description(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        await self.bot.send_message(chat_id, of.send_description())

    async def rules_handler(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        await self.bot.send_message(chat_id, of.send_rules())

    async def send_random_images_handler(self, callback_query: types.CallbackQuery):

        # Генерация картинок и запись отправленных в БД
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        image_list = img.open_random_images(chat_id, user_id)
        img.db_delete_sent_cards_in_turn(user_id, chat_id)
        if image_list:
            for image_bytes, image_path in image_list:
                # Генерация уникальных uuid для картинок
                uniq_id = img.generate_uuid()

                # Добавление картинки в базу данных
                img.add_image_to_database(uniq_id, user_id, chat_id, image_path, in_hand=True)

                message = await self.bot.send_photo(callback_query.from_user.id, photo=image_bytes,
                                                    reply_markup=kb.inline_kb3)
                file_id = message.photo[-1].file_id  # получаем file_id картинки на сервере телеграмма

                # Сохранение данных картинки в базу данных
                img.save_user_chat_to_db(uniq_id, user_id, chat_id, file_id)
                img.db_save_card_in_hand(uniq_id, user_id, file_id, in_hand=True)
                img.db_insert_user_done_turn(user_id, chat_id, sent_card=True)

            # Кнопка возврата в чат
            chat_link = await self.bot.export_chat_invite_link(chat_id=callback_query.message.chat.id)
            buttons = kb.Buttons()
            buttons.create_inline_kb4(chat_link=chat_link)
            inline_kb4 = buttons.inline_kb4

            # Отправка разделителя
            await self.bot.send_photo(callback_query.from_user.id, photo=of.dilimeter())

            await self.bot.send_message(callback_query.from_user.id, text='Нажми кнопку, чтобы вернуться в чат:',
                                        reply_markup=inline_kb4)
        else:
            await self.bot.send_message(callback_query.from_user.id, text='Все картинки уже были отправлены :(')
            await self.bot.send_message(callback_query.from_user.id, text='Нажми кнопку, чтобы вернуться в чат:',
                                        reply_markup=kb.inline_kb4)

    async def send_image_to_chat(self, callbackQuery: types.CallbackQuery):
        file_id = callbackQuery.message.photo[-1].file_id
        chat_id = images.get_mapp_user_chat(callbackQuery.from_user.id)
        file_info = await self.bot.get_file(file_id)
        user_id = callbackQuery.from_user.id
        image_url = f'https://api.telegram.org/file/bot{config.bot_token.get_secret_value()}/{file_info.file_path}'
        was_sent_img = img.check_image_in_db(file_id)
        was_sent_imgs = img.user_sent_cards_in_turn(user_id, chat_id, sent_card=False)
        if was_sent_img:
            await self.bot.send_message(callbackQuery.from_user.id, text='Эта карта уже была отправлена')
        elif was_sent_imgs:
            await self.bot.send_message(callbackQuery.from_user.id, text='Ты уже отправлял карты в этот ход')
        else:
            with requests.get(image_url, stream=True) as r:
                r.raise_for_status()
                with io.BytesIO(r.content) as image:
                    caption = 'Карточка от ' + callbackQuery.from_user.full_name
                    await self.bot.send_photo(chat_id=chat_id, photo=image, caption=caption)
                    in_hand = False
                    img.update_in_hand_flag(file_id, user_id, in_hand)
                    img.db_insert_user_sent_card(user_id, file_id)
                    img.db_update_user_done_turn(user_id, chat_id, sent_card=False)

    async def send_situation(self, callback_query: types.CallbackQuery):
        await self.bot.send_message(callback_query.message.chat.id, text=of.send_situation())

    async def delete_images_from_db(self, callback_query: types.CallbackQuery):
        deleted = img.delete_images_from_db(callback_query.from_user.id, callback_query.message.chat.id)
        await self.bot.send_message(callback_query.message.chat.id, text=deleted)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # логгирование
    bot = TelegramBot(token=config.bot_token.get_secret_value())
    executor.start_polling(bot.dp, skip_updates=True)
