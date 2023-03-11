from config_reader import config
from aiogram import Bot, Dispatcher, executor, types
import logging
import keyboard as kb
import open_files as of
import sqlite3

logging.basicConfig(level=logging.INFO)  # логгирование

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(of.send_welcome_text(), reply_markup=kb.inline_kb1)
    # await callback.answer()


@dp.callback_query_handler(lambda c: c.data == 'button_start_game')
async def start_game_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, text='Начинаем! Ситуация:')
    await bot.send_message(chat_id, text=of.send_situation())
    await bot.send_message(chat_id, 'Нажми на кнопку ниже, чтобы получить мемы', reply_markup=kb.inline_kb2)


@dp.callback_query_handler(lambda c: c.data == 'button_rules')
async def process_callback_button2(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, of.send_rules())
    # await callback.answer()

@dp.callback_query_handler(lambda c: c.data == 'button_get_memes')
async def send_random_images_handler(callback_query: types.CallbackQuery):
    image_bytes_list = of.open_random_images(callback_query=callback_query)
    if image_bytes_list:
        for image_bytes in image_bytes_list:
            await bot.send_photo(callback_query.from_user.id, photo=image_bytes)
    else:
        await bot.send_message(callback_query.from_user.id, text='Все картинки уже были отправлены :(')




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
