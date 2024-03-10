from aiogram.enums import ParseMode
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from db_music_bot import engine, Music
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from aiogram.utils.markdown import hbold
import asyncio
import logging
import sys

load_dotenv()

TOKEN = getenv('TOKEN')

dp = Dispatcher(storage=MemoryStorage())

lower_limit = 0

keyword = None


@dp.message(CommandStart())
async def start(message: types.Message) -> None:
    await message.answer(f"Salom {hbold(message.from_user.full_name)}")


@dp.message(F.content_type == ContentType.TEXT)
async def text(message: types.Message) -> None:
    global keyword
    global lower_limit
    lower_limit = 0
    keyword = message.text.lower()
    with Session(engine) as session:
        total_count = session.scalar(select(func.count()).where(
            Music.name.ilike(f"%{keyword}%")))
        data = session.scalars(select(Music).where(
            Music.name.ilike(f"%{keyword}%")).limit(10).offset(lower_limit)).all()
        count = 0
        builder = InlineKeyboardBuilder()
        caption = ""
        for music in data:
            count += 1
            builder.button(text=f"{count}", callback_data=f"button_{music.id}")
            caption += f"{count}. {music.performer}-{music.title}\n"
        if count == 0:
            await message.answer("Sorry, I couldn't find", reply_markup=builder.as_markup())
        else:

            if lower_limit == 0 and total_count > 10:
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count > lower_limit + 10:
                builder.button(text='<<',
                               callback_data=f'back')
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count < lower_limit:
                builder.button(text='<<',
                               callback_data=f'back')
            builder.adjust(5, repeat=True)
            await message.answer(caption, reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'forward')
async def forward(callback: types.CallbackQuery) -> None:
    global lower_limit
    lower_limit += 10
    global keyword
    with Session(engine) as session:
        total_count = session.scalar(select(func.count()).where(
            Music.name.ilike(f"%{keyword}%")))
        data = session.scalars(select(Music).where(
            Music.name.ilike(f"%{keyword}%")).limit(10).offset(lower_limit)).all()
        count = 0
        builder = InlineKeyboardBuilder()
        caption = ""
        count = lower_limit
        for music in data:
            count += 1
            builder.button(text=f"{count}", callback_data=f"button_{music.id}")
            caption += f"{count}. {music.performer}-{music.title}\n"
        if count == 0:
            await callback.message.edit_text("Sorry, I couldn't find", reply_markup=builder.as_markup())
        else:
            if lower_limit == 0 and total_count > 10:
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count > lower_limit + 10:
                builder.button(text='<<',
                               callback_data=f'back')
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count < lower_limit + 10:
                builder.button(text='<<',
                               callback_data=f'back')
            builder.adjust(5, repeat=True)
            await callback.message.edit_text(caption, reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'back')
async def back_callback(callback: types.CallbackQuery) -> None:
    global lower_limit
    lower_limit -= 10
    global keyword
    with Session(engine) as session:
        total_count = session.scalar(select(func.count()).where(
            Music.name.ilike(f"%{keyword}%")))
        data = session.scalars(select(Music).where(
            Music.name.ilike(f"%{keyword}%")).limit(10).offset(lower_limit)).all()
        count = 0
        builder = InlineKeyboardBuilder()
        caption = ""
        count = lower_limit
        for music in data:
            count += 1
            builder.button(text=f"{count}", callback_data=f"button_{music.id}")
            caption += f"{count}. {music.performer}-{music.title}\n"
        if count == 0:
            await callback.message.edit_text("Sorry, I couldn't find", reply_markup=builder.as_markup())
        else:
            if lower_limit == 0 and total_count > 10:
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count > lower_limit + 10:
                builder.button(text='<<',
                               callback_data=f'back')
                builder.button(text='>>',
                               callback_data=f'forward')
            elif lower_limit != 0 and total_count < lower_limit + 10:
                builder.button(text='<<',
                               callback_data=f'back')
            builder.adjust(5, repeat=True)
            await callback.message.edit_text(caption, reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith('button_'))
async def callback_query(callback: types.CallbackQuery) -> None:
    q_id = int(callback.data.split('_')[-1])
    with Session(engine) as session:
        music = session.query(Music).filter(Music.id == q_id).first()
        if music:
            await callback.message.answer_audio(music.file_id)


@dp.message(F.content_type == ContentType.AUDIO)
async def audio(message: types.Message) -> None:
    audio = message.audio
    name = audio.file_name
    title = audio.title
    performer = audio.performer
    duration = audio.duration
    file_id = audio.file_id
    with Session(engine) as session:
        session.add(Music(title=title, performer=performer, duration=duration, file_id=file_id, name=name))
        session.commit()
    await message.reply("Database ga qo'shildi")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
