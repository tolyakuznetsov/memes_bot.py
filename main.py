import asyncio
import io
import json
import logging

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext

import images
import images as img
import keyboard
import keyboard as kb
import open_files as of
import states
from config_reader import config


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.setup_handlers()
        self.dp.middleware.setup(LoggingMiddleware())
        self.button_test = None

    def setup_handlers(self):
        self.dp.register_message_handler(self.end_command_handler, commands=['end'], state='*')
        self.dp.register_message_handler(self.player_count_handler, state=states.UsersStates.wait_response)
        self.dp.register_message_handler(self.start_command_handler, commands=['start'])
        self.dp.register_callback_query_handler(self.start_game_handler, lambda c: c.data == 'button_start_game')
        self.dp.register_callback_query_handler(self.rules_handler, lambda c: c.data == 'button_rules')
        self.dp.register_callback_query_handler(self.send_random_images_handler, lambda c: c.data == 'button_get_memes')
        self.dp.register_callback_query_handler(self.send_situation, lambda c: c.data == 'button_get_situation')
        self.dp.register_callback_query_handler(self.send_image_to_chat,
                                                lambda query: query.data.startswith('image_path'))
        self.dp.register_callback_query_handler(self.send_description, lambda c: c.data == 'button_description')
        self.dp.register_callback_query_handler(self.user_pick_hero, lambda c: c.data.startswith('hero_'))
        self.dp.register_callback_query_handler(self.stop_pick_hero, lambda c: c.data == 'button_stop_pick_hero')

    @staticmethod
    async def start_command_handler(message: types.Message):
        chat_id = message.chat.id
        if chat_id == 274921311:
            await message.reply('Привет! Я бот для игры в ..., добавь меня в чат, чтобы начать игру',
                                reply_markup=kb.inline_kb6)
        else:
            await message.reply(of.send_welcome_text(), reply_markup=kb.inline_kb1)

    @staticmethod
    async def end_command_handler(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        chat_id = message.chat.id
        deleted = img.delete_images_from_db(user_id, chat_id)
        await message.reply(deleted)
        await state.finish()

    async def start_game_handler(self, callback_query: types.CallbackQuery):
        chat_id = callback_query.message.chat.id
        user_full_name = callback_query.from_user.full_name
        message_id = callback_query.message.message_id
        message = f'{user_full_name}, сколько игроков будет участвовать?'
        await states.UsersStates.wait_response.set()
        await self.bot.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=callback_query.message.message_id, reply_markup=None)
        await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await self.bot.send_message(chat_id, text=message)

    @staticmethod
    async def player_count_handler(message: types.Message, state: FSMContext):
        player_count = message.text
        chat_id = message.chat.id
        user_id = message.from_user.id
        _keyboard = 'inline_kb_pers'

        button = kb.Buttons().create_inline_kb_pers(int(player_count))
        if player_count.isdigit():
            await message.answer('Отлично! Разбирайте персонажей:', reply_markup=button)
            img.db_insert_keyboard(_keyboard, chat_id, user_id, str(button))
        else:
            await message.answer("Пожалуйста, укажи число игроков")

        await state.finish()

    async def user_pick_hero(self, callback_query: types.CallbackQuery):
        button_data = callback_query.data
        hero = str(button_data).replace('hero_', '')
        user_name = callback_query.from_user.full_name
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        message_id = callback_query.message.message_id
        _keyboard = 'inline_kb_pers'

        users_hero = img.db_select_user_hero(chat_id, user_id)
        if users_hero:
            await self.bot.send_message(chat_id, f'{user_name}, ты уже выбрал {users_hero}')
        else:
            # Записываем в БД героя, которого выбрал юзер
            img.db_insert_user_hero(chat_id, user_id, hero)

            # Получаем сохраненную клавиатуру и удаляем нажатую кнопку
            last_keyboard = img.db_select_keyboard(_keyboard, chat_id)
            last_keyboard['inline_keyboard'] = [x for x in last_keyboard["inline_keyboard"] if
                                                not any(y["callback_data"] == button_data for y in x)]

            last_keyboard_for_save = {"inline_keyboard": last_keyboard["inline_keyboard"]}
            img.db_update_keyboard(json.dumps(last_keyboard_for_save), _keyboard, chat_id)

            # Отправляем обновленную клавиатуру
            await self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=last_keyboard)
            await self.bot.send_message(chat_id, f'{user_name} выбрал {hero}')

            if len(last_keyboard['inline_keyboard']) == 1 and last_keyboard['inline_keyboard'][0][0]['callback_data'] \
                    == 'button_stop_pick_hero':
                img.db_delete_keyboard(_keyboard, chat_id)

    async def stop_pick_hero(self, callback_query: types.CallbackQuery):

        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        _keyboard = 'inline_kb_pers'

        count_users = img.db_select_check_count_players(chat_id)

        if not count_users:
            await self.bot.send_message(chat_id, text='Вы не выбрали персонажей')
        else:
            img.db_delete_keyboard(_keyboard, chat_id)

            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await self.bot.send_message(chat_id, text='Начинаем игру', reply_markup=keyboard.inline_kb2)

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
        message_id = callback_query.message.message_id
        callback_data = callback_query.data

        current_keyboard = callback_query.message.reply_markup
        update_keyboard = keyboard.buttons.delete_button(current_keyboard, callback_data)

        await self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=update_keyboard)

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

        chat_id = callback_query.message.chat.id
        sit = of.send_situation(chat_id)
        img.db_insert_situation(chat_id, sit)
        message_id = callback_query.message.message_id
        callback_data = callback_query.data
        current_keyboard = callback_query.message.reply_markup
        update_keyboard = keyboard.buttons.delete_button(current_keyboard, callback_data)

        await self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=update_keyboard)

        await self.bot.send_message(chat_id, text=sit)

        # Отправляем сообщение о том, что пользователю дается 30 секунд на выбор карты
        message_30_sec = await self.bot.send_message(chat_id, text='У вас 30 секунд на отправку карт в чат!')

        # Ждем 20 секунд и отправляем сообщение о том, что осталось 10 секунд
        await asyncio.sleep(20)
        message_10_sec = await self.bot.send_message(chat_id, text='Осталось 10 секунд!')

        # Ждем еще 10 секунд и отправляем опрос
        await asyncio.sleep(10)
        await self.bot.send_poll(chat_id=chat_id,
                                 question='Кто победил?',
                                 options=['Игрок 1', 'Игрок 2', 'Игрок 3'],
                                 is_anonymous=False)

        # Удаляем сообщения о таймере
        await self.bot.delete_message(chat_id, message_30_sec.message_id)
        await self.bot.delete_message(chat_id, message_10_sec.message_id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # логгирование
    bot = TelegramBot(token=config.bot_token.get_secret_value())
    executor.start_polling(bot.dp, skip_updates=True)
