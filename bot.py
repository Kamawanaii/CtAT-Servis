import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

cart = {}

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Добро пожаловать! Напиши /catalog")

@dp.message(Command("catalog"))
async def catalog(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/products") as resp:
            products = await resp.json()

    for p in products:
        await message.answer(f"{p['name']} - {p['price']} ₽")

@dp.message(Command("order"))
async def order(message: Message):
    await bot.send_message(ADMIN_ID, f"Новый заказ от {message.from_user.id}")
    await message.answer("Заказ отправлен!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
