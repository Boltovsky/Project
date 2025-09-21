# Set-ExecutionPolicy RemoteSigned --CurrentUser

import os
import sqlite3
import aiogram
import asyncio
from aiogram import F, Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello!")

@dp.message(Command('help')) #/help
async def cmd_help(message: Message):
    await message.answer(f'Ваш chat_id:{message.chat.id}')
# @dp.message(F.text == 'Привет') 
# async def call_me(message: Message):
#     await bot.send_message(ADMIN_CHAT_ID,f'Вам пишет {message.from_user.username}')

async def send_message_async(text:str):
    await bot.send_message(ADMIN_CHAT_ID, text=text)

def send_message(text:str,comment_id):
    async def _send():
        bot_temp = Bot(token=TOKEN)
        await bot_temp.send_message(ADMIN_CHAT_ID, text=text, parse_mode='html',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Подтвердить', callback_data=f'verify_{comment_id}'),
                                                                                                                                    InlineKeyboardButton(text='Отклонить', callback_data=f'delete_{comment_id}')]]))
        await bot_temp.session.close()
    asyncio.run(_send())

@dp.callback_query(F.data.startswith('verify'))
async def verify_comment(callback: CallbackQuery):
    comment_id = int(callback.data[7:])
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('UPDATE gamenews_comment SET verify=1 WHERE id =?;',(comment_id,))
    conn.commit()
    conn.close()
    await callback.answer()
    await callback.message.answer(f'Коммент с айди:{comment_id} был норм!')
    await callback.message.edit_reply_markup(reply_markup=None)
@dp.callback_query(F.data.startswith('delete'))
async def verify_comment(callback: CallbackQuery):
    comment_id = int(callback.data[7:])
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gamenews_comment WHERE id =?;',(comment_id,))
    conn.commit()
    conn.close()
    await callback.answer()
    await callback.message.answer(f'Коммент с айди:{comment_id} был уничтожен!')
    await callback.message.edit_reply_markup(reply_markup=None)


async def main():
    await send_message_async('Бот попущен и готов ко всему!')
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен!")
    except Exception as e:
        print(f"Ошибка: {e}")
