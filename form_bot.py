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
from db_form_bot import engine, Form
from sqlalchemy.orm import Session
from sqlalchemy import select
from aiogram.utils.markdown import hbold
import asyncio
import logging
import sys

load_dotenv()

TOKEN = getenv('TOKEN')

dp = Dispatcher(storage=MemoryStorage())

is_user_old = False


class FormState(StatesGroup):
    name = State()
    age = State()
    photo = State()


@dp.message(CommandStart())
async def start(message: types.Message) -> None:
    btn = InlineKeyboardButton(text="form", callback_data="button1")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    await message.answer(f"Salom, {hbold(message.from_user.full_name)}!\n form ni to'ldiring", reply_markup=keyboard)


@dp.callback_query(F.data == "button1")
async def form(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(f"ismingizni kiriting")
    await state.set_state(FormState.name)


@dp.message(F.content_type == ContentType.TEXT, FormState.name)
async def form(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(f"yoshingizni kiriting")
    await state.set_state(FormState.age)


@dp.message(F.content_type == ContentType.TEXT, FormState.age)
async def form(message: types.Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("Xato yosh\nYoshingizni qaytadan kiriting")
        return
    await state.update_data(age=message.text)
    await message.answer(f"rasmingizni jo`nating")
    await state.set_state(FormState.photo)


@dp.message(F.content_type == ContentType.PHOTO, FormState.photo)
async def form(message: types.Message, state: FSMContext) -> None:
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("Rasmingiz qabul qilindi va forma shakillantirildi")
    data = await state.get_data()
    name = data['name']
    age = data['age']
    photo = data['photo']
    await message.answer_photo(photo, f'Name: {name}\nAge: {age}\n')
    await state.clear()
    with Session(engine) as session:
        session.add(Form(name=name, age=age, photo=photo, user_id=str(message.from_user.id)))
        session.commit()


@dp.message(Command('get_forms'), F.from_user.id == 5091336899)
async def get_forms(message: types.Message) -> None:
    with Session(engine) as session:
        data = session.scalars(select(Form)).all()
    if not data:
        await message.answer("No forms found")
    else:
        for f in data:
            await message.answer_photo(f.photo,
                                       caption=f'''Id: {hbold(f.id)}\nIsmi: {hbold(f.name)}\nYoshi: {hbold(f.age)}\nFoydalanuvchi: <a href="tg://user?id={hbold(f.user_id)}">{hbold(f.user_id)}</a>\nYaratilgan vatqi: {hbold(f.created_at)}''')


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
