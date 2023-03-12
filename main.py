from config_reader import config
from aiogram import Bot, Dispatcher, executor, types
import logging
import keyboard as kb
import open_files as of
import images as img
import requests
import io

logging.basicConfig(level=logging.INFO)  # логгирование

telegram_api_path = f'https://api.telegram.org/file/bot{config.bot_token.get_secret_value()}/'

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
    await bot.send_message(chat_id, 'Нажми на кнопку ниже, чтобы получить мемы, а потом перейди в бота, '
                                    'чтобы разыграть карты', reply_markup=kb.inline_kb2)
    await bot.send_message(chat_id, 'Для перехода в бота:', reply_markup=kb.button_go_to_bot)


@dp.callback_query_handler(lambda c: c.data == 'button_rules')
async def process_callback_button2(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, of.send_rules())
    # await callback.answer()


@dp.callback_query_handler(lambda c: c.data == 'button_get_memes')
async def send_random_images_handler(callback_query: types.CallbackQuery):
    image_bytes_list = img.open_random_images(callback_query=callback_query)
    if image_bytes_list:
        for image_bytes in image_bytes_list:
            await bot.send_photo(callback_query.from_user.id, photo=image_bytes, reply_markup=kb.inline_kb3)
    else:
        await bot.send_message(callback_query.from_user.id, text='Все картинки уже были отправлены :(')


@dp.callback_query_handler(lambda c: c.data == 'button_get_memes')
async def get_chat_id(callback_query: types.CallbackQuery):
    chat_id_2 = callback_query.message.chat.id
    print(chat_id_2)



'''@dp.callback_query_handler(lambda query: query.data.startswith('image_path'))
async def send_image_to_chat(query: types.CallbackQuery):
    file_id = query.message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    image_url = f'https://api.telegram.org/file/bot{config.bot_token.get_secret_value()}/{file_info.file_path}'

    with requests.get(image_url, stream=True) as r:
        r.raise_for_status()
        with io.BytesIO(r.content) as image:
            await bot.send_photo(, photo=image)'''





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
