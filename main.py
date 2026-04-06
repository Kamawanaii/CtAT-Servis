from fastapi import FastAPI, UploadFile
import pandas as pd
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

app = FastAPI()

products = []

# ===== TELEGRAM BOT =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/products")
def get_products():
    return products

@app.post("/upload")
def upload(file: UploadFile):
    global products
    df = pd.read_excel(file.file)
    products = df.to_dict(orient="records")
    return {"status": "ok"}

# ===== BOT HANDLERS =====

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Магазин работает ✅\n/catalog")

@dp.message(Command("catalog"))
async def catalog(message: Message):
    if not products:
        await message.answer("Товаров нет")
        return

    for p in products:
        await message.answer(f"{p['name']} — {p['price']} ₽")

@dp.message(Command("order"))
async def order(message: Message):
    await bot.send_message(ADMIN_ID, f"🛒 Заказ от {message.from_user.id}")
    await message.answer("Заказ отправлен!")

# ===== START BOT INSIDE FASTAPI =====

async def start_bot():
    await dp.start_polling(bot)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_bot())
