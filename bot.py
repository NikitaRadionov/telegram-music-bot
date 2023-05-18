import os, bd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from hosts import HOSTS
from secure_data import BOT_TOKEN
from messages import *


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text=START_MESSAGE, parse_mode="HTML")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_MESSAGE, parse_mode="HTML")


@dp.callback_query_handler()
async def download_track(callback: types.CallbackQuery):

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.send_message(callback.message.chat.id, text=PLEASE_WAIT, parse_mode="HTML")

    host = callback.data
    q = callback.message.text.split("\"")[1]
    artist, title = q.split(" - ")
    is_success = await HOSTS[host]().download_file(q)

    if is_success:
        await callback.message.answer(text=SUCCESS_GETTING_FILE, parse_mode="HTML")
    else:
        return await callback.message.answer(text=NOT_FOUND_MESSAGE, parse_mode="HTML")

    path = os.path.abspath(os.path.dirname(__file__)) + f'/media/music/{q}.mp3'

    connection = await bd.connect()

    await bd.insert_into_bd(connection, title, artist, path)
    await connection.close()

    await bot.send_audio(callback.message.chat.id, audio=open(path, 'rb'))



def get_inline_keyboard():
    ikb = InlineKeyboardMarkup(row_width=3)
    ib1 = InlineKeyboardButton(text='Сторонний источник',
                            callback_data='Drive')
    ikb.add(ib1)
    return ikb


@dp.message_handler()
async def find(message: types.Message):

    q = message.text

    if q.count("-") != 1:
        return await message.answer(text=WRONG_REQUEST_MESSAGE, parse_mode="HTML")

    artist, title = q.split(" - ")

    connection = await bd.connect()

    results = await bd.select_from_bd(connection, title, artist)

    await connection.close()

    if len(results) > 0:
        result = results[0]
        await message.answer(text=FILE_FOUND_ON_SERVER, parse_mode="HTML")
        await bot.send_audio(message.from_user.id, audio=open(result['path'], 'rb'))
    else:

        ikb = get_inline_keyboard()
        CHOOSE_SOURCE = f"<b>Трека \"{q}\" нет в моей базе. Где будем искать ?</b>\n\n<b>Выберите источник:</b>"

        await message.answer(text=CHOOSE_SOURCE,
                            parse_mode="HTML",
                            reply_markup=ikb)


if __name__ == "__main__":
    executor.start_polling(dp)