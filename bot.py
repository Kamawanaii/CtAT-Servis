import asyncio
import aiohttp
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

cart = {}
user_index = {}

# ---------- MAIN MENU ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")]
    ])

# ---------- PRODUCT MENU ----------
def product_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data="prev"),
            InlineKeyboardButton(text="➕ В корзину", callback_data="add"),
            InlineKeyboardButton(text="➡️", callback_data="next"),
        ],
        [
            InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")
        ]
    ])

# ---------- START ----------
@dp.message()
async def start(message: Message):
    await message.answer("Добро пожаловать 👋", reply_markup=main_menu())

# ---------- LOAD PRODUCTS ----------
async def get_products():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/products") as resp:
            return await resp.json()

# ---------- OPEN CATALOG ----------
@dp.callback_query(F.data == "catalog")
async def catalog(callback: CallbackQuery):
    products = await get_products()

    user_index[callback.from_user.id] = 0
    i = 0
    p = products[i]

    text = f"{p['name']}\n💰 {p['price']} ₽"

    await callback.message.edit_text(text, reply_markup=product_kb())
    await callback.answer()

# ---------- NEXT ----------
@dp.callback_query(F.data == "next")
async def next_product(callback: CallbackQuery):
    products = await get_products()
    uid = callback.from_user.id

    i = user_index.get(uid, 0)
    i = (i + 1) % len(products)
    user_index[uid] = i

    p = products[i]
    text = f"{p['name']}\n💰 {p['price']} ₽"

    await callback.message.edit_text(text, reply_markup=product_kb())
    await callback.answer()

# ---------- PREV ----------
@dp.callback_query(F.data == "prev")
async def prev_product(callback: CallbackQuery):
    products = await get_products()
    uid = callback.from_user.id

    i = user_index.get(uid, 0)
    i = (i - 1) % len(products)
    user_index[uid] = i

    p = products[i]
    text = f"{p['name']}\n💰 {p['price']} ₽"

    await callback.message.edit_text(text, reply_markup=product_kb())
    await callback.answer()

# ---------- ADD TO CART ----------
@dp.callback_query(F.data == "add")
async def add(callback: CallbackQuery):
    products = await get_products()
    uid = callback.from_user.id

    i = user_index.get(uid, 0)
    product = products[i]

    user_cart = cart.setdefault(uid, [])

    for item in user_cart:
        if item["name"] == product["name"]:
            item["qty"] += 1
            break
    else:
        user_cart.append({
            "name": product["name"],
            "price": product["price"],
            "qty": 1
        })

    await callback.answer("Добавлено 🛒")

# ---------- CART ----------
def cart_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="order")],
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")]
    ])

@dp.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    user_cart = cart.get(callback.from_user.id, [])

    if not user_cart:
        await callback.message.edit_text("Корзина пуста", reply_markup=main_menu())
        return

    text = "🛒 Ваша корзина:\n\n"
    total = 0

    for item in user_cart:
        total += item["price"] * item["qty"]
        text += f"{item['name']} x{item['qty']}\n"

    text += f"\n💰 Итого: {total} ₽"

    await callback.message.edit_text(text, reply_markup=cart_kb())
    await callback.answer()

# ---------- ORDER ----------
@dp.callback_query(F.data == "order")
async def order(callback: CallbackQuery):
    user_cart = cart.get(callback.from_user.id, [])

    if not user_cart:
        await callback.answer("Корзина пуста")
        return

    text = "🛒 НОВЫЙ ЗАКАЗ\n\n"
    total = 0

    for item in user_cart:
        total += item["price"] * item["qty"]
        text += f"{item['name']} x{item['qty']}\n"

    text += f"\n💰 Сумма: {total} ₽"

    await bot.send_message(ADMIN_ID, text)

    cart[callback.from_user.id] = []

    await callback.message.edit_text("Заказ отправлен ✅", reply_markup=main_menu())

# ---------- START BOT ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
