import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
# Хостинги обычно передают токен через переменную окружения BOT_TOKEN
# Это безопаснее, чем писать токен в коде.
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    # Если переменной нет (например, при локальном запуске), спросим в консоли
    API_TOKEN = input("Введите токен бота: ")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ДАННЫЕ (цены, балансы) ---
SPLIT_BALANCES = {
    "30": 30_000,
    "50": 50_000,
    "75": 75_000,
    "100": 100_000,
    "150": 150_000
}

def get_split_price(balance_thousands):
    balance_rub = balance_thousands * 1000
    price_rub = balance_rub * 0.05
    price_usd = price_rub / 90
    price_ton = price_rub / 350
    return f"{int(price_rub)} RUB / {round(price_usd, 2)} USD / {round(price_ton, 2)} TON"

PRODUCTS = {
    "corporate": {"name": "Корпоративный счет Яндекс", "price": "5000 RUB / 55 USD / 14 TON"},
    "carsharing": {"name": "Аккаунт Яндекс Каршеринг", "price": "1500 RUB / 16.5 USD / 4.3 TON"}
}

PAYMENT_INSTRUCTIONS = {
    "usdt": "💵 *Оплата USDT (TRC20)*\n\nПереведите точную сумму на кошелек:\n`ТВОЙ_КОШЕЛЕК_USDT`\n\nПосле оплаты нажмите кнопку поддержки и напишите код товара.\n\n⏳ Проверка ручная — в течение 24 часов с вами свяжется поддержка.",
    "ton": "💎 *Оплата TON*\n\nПереведите точную сумму на кошелек:\n`ТВОЙ_КОШЕЛЕК_TON`\n\nПосле оплаты нажмите кнопку поддержки и напишите код товара.\n\n⏳ Проверка ручная — в течение 24 часов с вами свяжется поддержка.",
    "card": "💳 *Оплата банковской картой РФ*\n\nПереведите точную сумму на карту:\n`2202 2036 xxxx xxxx`\n\nПосле оплаты нажмите кнопку поддержки и напишите код товара.\n\n⏳ Проверка ручная — в течение 24 часов с вами свяжется поддержка."
}

# --- КЛАВИАТУРЫ (как в прошлый раз, но с одним исправлением) ---
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📦 Каталог", callback_data="catalog"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    return builder.as_markup()

def catalog_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔹 Яндекс Сплит", callback_data="product_split"))
    builder.row(InlineKeyboardButton(text="🏢 Корпоративный счет", callback_data="product_corporate"))
    builder.row(InlineKeyboardButton(text="🚗 Яндекс Каршеринг", callback_data="product_carsharing"))
    builder.row(InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu"))
    return builder.as_markup()

def split_balance_keyboard():
    builder = InlineKeyboardBuilder()
    for balance in ["30", "50", "75", "100", "150"]:
        builder.row(InlineKeyboardButton(text=f"{balance} тыс. руб", callback_data=f"split_balance_{balance}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад в каталог", callback_data="catalog"))
    return builder.as_markup()

def payment_methods_keyboard(product_info):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💵 Оплатить USDT", callback_data=f"pay_usdt|{product_info}"))
    builder.row(InlineKeyboardButton(text="💎 Оплатить TON", callback_data=f"pay_ton|{product_info}"))
    builder.row(InlineKeyboardButton(text="💳 Оплатить картой", callback_data=f"pay_card|{product_info}"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    builder.row(InlineKeyboardButton(text="◀️ В каталог", callback_data="catalog"))
    return builder.as_markup()

def after_payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🆘 Связаться с поддержкой", callback_data="support"))
    builder.row(InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ КОМАНД (без if __name__ == "__main__" в конце) ---
@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = ("👋 *Добро пожаловать!*\n\nУ нас можно купить:\n"
                    "🔹 Яндекс Сплит — баланс от 30к до 150к руб. Цена: 5% от баланса\n"
                    "🔹 Корпоративные счета Яндекса — 5000 руб\n"
                    "🔹 Аккаунты Яндекс Каршеринга — 1500 руб\n\nВыберите действие:")
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

@dp.callback_query(lambda c: c.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("👋 *Главное меню*\n\nВыберите действие:", parse_mode="Markdown", reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.message.edit_text("📦 *Каталог товаров*\n\nВыберите нужный товар:", parse_mode="Markdown", reply_markup=catalog_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text("🆘 *Поддержка*\n\nСвяжитесь с нами: @your_support_username\n\nПо всем вопросам оплаты и получения товаров пишите сюда.", parse_mode="Markdown", reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "product_split")
async def product_split(callback: CallbackQuery):
    await callback.message.edit_text("🔹 *Яндекс Сплит*\n\nВыберите баланс счета (в тысячах рублей):\nЦена = 5% от баланса", parse_mode="Markdown", reply_markup=split_balance_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("split_balance_"))
async def split_balance_selected(callback: CallbackQuery):
    balance = callback.data.split("_")[2]
    balance_thousands = int(balance)
    price = get_split_price(balance_thousands)
    product_info = f"split|{balance}"
    text = (f"🔹 *Яндекс Сплит*\n📊 Баланс счета: *{balance} тыс. руб* ({balance_thousands * 1000} руб)\n💰 Цена (5%): *{price}*\n\nВыберите способ оплаты:")
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard(product_info))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("product_") and c.data != "product_split")
async def other_products(callback: CallbackQuery):
    product_key = callback.data.split("_")[1]
    product = PRODUCTS[product_key]
    product_info = f"{product_key}|none"
    text = (f"🛒 *{product['name']}*\n\n💰 Стоимость: *{product['price']}*\n\nВыберите способ оплаты:")
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard(product_info))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("pay_"))
async def payment_method(callback: CallbackQuery):
    data = callback.data
    _, method, product_info = data.split("|")
    instruction = PAYMENT_INSTRUCTIONS.get(method, "Инструкция отсутствует")
    if product_info.startswith("split"):
        balance = product_info.split("|")[1]
        balance_rub = int(balance) * 1000
        price = int(balance_rub * 0.05)
        text = (f"🔹 *Яндекс Сплит* | Баланс: {balance} тыс. руб\n💰 Сумма к оплате: *{price} руб* / {round(price/90,2)} USD / {round(price/350,2)} TON\n\n{instruction}\n\nПосле оплаты нажмите на кнопку поддержки и укажите товар и сумму.")
    elif product_info.startswith("corporate"):
        text = (f"🏢 *Корпоративный счет Яндекс*\n💰 Сумма к оплате: *5000 руб* / 55 USD / 14 TON\n\n{instruction}\n\nПосле оплаты нажмите на кнопку поддержки и укажите товар.")
    elif product_info.startswith("carsharing"):
        text = (f"🚗 *Яндекс Каршеринг*\n💰 Сумма к оплате: *1500 руб* / 16.5 USD / 4.3 TON\n\n{instruction}\n\nПосле оплаты нажмите на кнопку поддержки и укажите товар.")
    else:
        text = f"{instruction}\n\nПосле оплаты нажмите поддержку."
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=after_payment_keyboard())
    await callback.answer()

# --- ЗАПУСК БОТА (эта часть важна для хостинга) ---
async def main():
    # Удаляем старые вебхуки и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Точка входа для хостинга
if __name__ == "__main__":
    asyncio.run(main())
