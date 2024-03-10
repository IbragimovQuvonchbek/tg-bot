from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.filters import CommandStart
import asyncio
import logging
import sys
from weather_helper import weather
from aiogram.types import URLInputFile

load_dotenv()

TOKEN = getenv('TOKEN')

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Weather Bot")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        mes = message.text
        city = weather(mes)
        image = URLInputFile(
            f"https://openweathermap.org/img/wn/{city[2]}@2x.png",
            filename=f"{city[2]}.png"
        )
        await message.answer_photo(image, caption=city[1])
    except Exception:
        await message.answer("Wrong City name")


async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
