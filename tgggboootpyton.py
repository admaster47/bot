import logging
import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

# --- НАСТРОЙКИ ---
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    API_TOKEN = input("Введите токен бота: ")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище заказов (в реальном проекте используйте БД)
user_orders = {}

# --- ДАННЫЕ ---
SPLIT_BALANCES = {
    "30": 30_000,
    "50": 50_000,
    "75": 75_000,
    "100": 100_000,
    "150": 150_000
}

# Курсы (можно обновлять вручную)
USD_RUB = 90
TON_RUB = 350
STAR_RUB = 1.4

def get_split_price_rub(balance_thousands):
    balance_rub = balance_thousands * 1000
    return int(balance_rub * 0.05)  # цена в рублях

def convert_to_usd(rub):
    return rub // USD_RUB  # округление в меньшую сторону до целого

def convert_to_ton(rub):
    ton = rub / TON_RUB
    return int(ton // 0.5) * 0.5  # округление в меньшую сторону до 0.5

def convert_to_stars(rub):
    return int(rub // STAR_RUB)  # округление в меньшую сторону

PRODUCTS = {
    "split": {"name": "Яндекс Сплит"},
    "corporate": {"name": "Корпоративный счет Яндекс", "price_rub": 5000},
    "carsharing": {"name": "Аккаунт Яндекс Каршеринг", "price_rub": 1500}
}

# Реквизиты (замените на свои)
CRYPTO_WALLETS = {
    "usdt": "TX7xxxxxxxxxxxxxxxxxxxxxYZ",
    "ton": "EQDxxxxxxxxxxxxxxxxxxxxxyz"
}
PAYMENT_SITE = "https://example.com/pay"  # замените на ваш сайт
PAYMENT_USERNAME = "your_game_username"  # замените на ваш юзернейм

# --- ГЛАВНОЕ МЕНЮ СНИЗУ (ReplyKeyboard) ---
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="📦 Каталог")],
        [KeyboardButton(text="🆘 Поддержка")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# --- Inline-клавиатуры ---
def catalog_inline_keyboard():
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
    builder.row(InlineKeyboardButton(text="◀️ Назад в каталог", callback_data="catalog_back"))
    return builder.as_markup()

def payment_methods_keyboard(product_type, product_data):
    """product_data: для сплита это баланс, для других - цена в руб"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💵 Оплатить USDT", callback_data=f"pay_usdt|{product_type}|{product_data}"))
    builder.row(InlineKeyboardButton(text="💎 Оплатить TON", callback_data=f"pay_ton|{product_type}|{product_data}"))
    builder.row(InlineKeyboardButton(text="💳 Оплатить картой (звезды)", callback_data=f"pay_card|{product_type}|{product_data}"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support_inline"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="catalog_back"))
    return builder.as_markup()

def back_to_catalog_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Вернуться в каталог", callback_data="catalog_back"))
    return builder.as_markup()

# --- ГЕНЕРАЦИЯ НОМЕРА ЗАКАЗА ---
def generate_order_number(user_id):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(100, 999)
    order_num = f"{timestamp}{user_id}{random_num}"[-12:]
    return order_num

def save_order(user_id, order_num, product_info, amount_rub, amount_usd, amount_ton, amount_stars):
    user_orders[order_num] = {
        "user_id": user_id,
        "product": product_info,
        "amount_rub": amount_rub,
        "amount_usd": amount_usd,
        "amount_ton": amount_ton,
        "amount_stars": amount_stars,
        "status": "pending",
        "created_at": datetime.now()
    }
    return order_num

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "👋 *Добро пожаловать в магазин!*\n\n"
        "📦 *Что у нас можно купить:*\n"
        "🔹 *Яндекс Сплит* — баланс от 30к до 150к руб.\n"
        "   💰 Цена: 5% от баланса\n"
        "🏢 *Корпоративный счет Яндекс* — 5000 руб\n"
        "🚗 *Аккаунт Яндекс Каршеринг* — 1500 руб\n\n"
        "💸 *Оплата:* USDT, TON или звезды ВК\n\n"
        "👇 *Нажмите кнопку «Каталог» ниже*"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@dp.message(lambda message: message.text == "📦 Каталог")
async def catalog_handler(message: types.Message):
    await message.answer("📦 *Каталог товаров*\n\nВыберите нужный товар:", parse_mode="Markdown", reply_markup=catalog_inline_keyboard())

@dp.message(lambda message: message.text == "🆘 Поддержка")
async def support_handler(message: types.Message):
    await message.answer(
        "🆘 *Поддержка*\n\nСвяжитесь с нами: @your_support_username\n\n"
        "📌 *Что указать при обращении:*\n"
        "• Номер заказа (выдается при выборе оплаты)\n"
        "• Сумму и способ оплаты\n\n"
        "⏳ *Время выдачи:* в течение 24 часов после оплаты",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(lambda c: c.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "👋 *Главное меню*\n\nВыберите действие в меню ниже:",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "catalog_back")
async def catalog_back_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 *Каталог товаров*\n\nВыберите нужный товар:",
        parse_mode="Markdown",
        reply_markup=catalog_inline_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "product_split")
async def product_split_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔹 *Яндекс Сплит*\n\nВыберите баланс счета (в тысячах рублей):\n💰 Цена = 5% от баланса",
        parse_mode="Markdown",
        reply_markup=split_balance_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("split_balance_"))
async def split_balance_callback(callback: CallbackQuery):
    balance = callback.data.split("_")[2]
    balance_thousands = int(balance)
    price_rub = get_split_price_rub(balance_thousands)
    price_usd = convert_to_usd(price_rub)
    price_ton = convert_to_ton(price_rub)
    
    product_data = f"balance_{balance}"
    text = (
        f"🔹 *Яндекс Сплит*\n"
        f"📊 Баланс счета: *{balance} тыс. руб* ({balance_thousands * 1000} руб)\n"
        f"💰 Стоимость:\n"
        f"   • {price_rub} RUB\n"
        f"   • {price_usd} USD\n"
        f"   • {price_ton} TON\n"
        f"   • {convert_to_stars(price_rub)} звезд\n\n"
        f"👇 Выберите способ оплаты:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard("split", product_data))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("product_corporate") or c.data.startswith("product_carsharing"))
async def other_products_callback(callback: CallbackQuery):
    product_key = callback.data.split("_")[1]
    product = PRODUCTS[product_key]
    price_rub = product["price_rub"]
    price_usd = convert_to_usd(price_rub)
    price_ton = convert_to_ton(price_rub)
    
    text = (
        f"🛒 *{product['name']}*\n\n"
        f"💰 Стоимость:\n"
        f"   • {price_rub} RUB\n"
        f"   • {price_usd} USD\n"
        f"   • {price_ton} TON\n"
        f"   • {convert_to_stars(price_rub)} звезд\n\n"
        f"👇 Выберите способ оплаты:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=payment_methods_keyboard(product_key, price_rub))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("pay_"))
async def payment_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, method, product_type, product_data = callback.data.split("|")
    
    # Определяем сумму в рублях
    if product_type == "split":
        balance = int(product_data.split("_")[1]) * 1000
        amount_rub = get_split_price_rub(balance // 1000)
        product_info = f"Яндекс Сплит (баланс: {balance // 1000} тыс. руб)"
    elif product_type == "corporate":
        amount_rub = 5000
        product_info = "Корпоративный счет Яндекс"
    elif product_type == "carsharing":
        amount_rub = 1500
        product_info = "Аккаунт Яндекс Каршеринг"
    else:
        amount_rub = int(product_data)
        product_info = product_type
    
    amount_usd = convert_to_usd(amount_rub)
    amount_ton = convert_to_ton(amount_rub)
    amount_stars = convert_to_stars(amount_rub)
    
    # Генерируем номер заказа
    order_num = generate_order_number(user_id)
    save_order(user_id, order_num, product_info, amount_rub, amount_usd, amount_ton, amount_stars)
    
    # Формируем сообщение с инструкцией
    if method == "usdt":
        instruction = (
            f"💵 *Оплата USDT (TRC20)*\n\n"
            f"📋 *Номер заказа:* `{order_num}`\n"
            f"🛒 *Товар:* {product_info}\n"
            f"💰 *Сумма к оплате:* {amount_usd} USDT\n\n"
            f"📍 *Реквизиты для перевода:*\n"
        )
        await callback.message.edit_text(instruction, parse_mode="Markdown", reply_markup=back_to_catalog_keyboard())
        # Отдельное сообщение с кошельком
        await callback.message.answer(
            f"🏦 *Кошелек USDT (TRC20):*\n`{CRYPTO_WALLETS['usdt']}`\n\n"
            f"✅ *После оплаты:*\n"
            f"1. Сохраните номер заказа: `{order_num}`\n"
            f"2. Напишите поддержке: @your_support_username\n"
            f"3. Укажите номер заказа и дату/время перевода\n\n"
            f"⏳ *Срок выдачи:* в течение 24 часов после подтверждения оплаты\n\n"
            f"🔓 После проверки вы получите полный доступ к аккаунту.",
            parse_mode="Markdown"
        )
        
    elif method == "ton":
        instruction = (
            f"💎 *Оплата TON*\n\n"
            f"📋 *Номер заказа:* `{order_num}`\n"
            f"🛒 *Товар:* {product_info}\n"
            f"💰 *Сумма к оплате:* {amount_ton} TON\n\n"
            f"📍 *Реквизиты для перевода:*\n"
        )
        await callback.message.edit_text(instruction, parse_mode="Markdown", reply_markup=back_to_catalog_keyboard())
        await callback.message.answer(
            f"🏦 *Кошелек TON:*\n`{CRYPTO_WALLETS['ton']}`\n\n"
            f"✅ *После оплаты:*\n"
            f"1. Сохраните номер заказа: `{order_num}`\n"
            f"2. Напишите поддержке: @your_support_username\n"
            f"3. Укажите номер заказа и дату/время перевода\n\n"
            f"⏳ *Срок выдачи:* в течение 24 часов после подтверждения оплаты\n\n"
            f"🔓 После проверки вы получите полный доступ к аккаунту.",
            parse_mode="Markdown"
        )
        
    elif method == "card":
        instruction = (
            f"💳 *Оплата банковской картой (через звезды ВК)*\n\n"
            f"📋 *Номер заказа:* `{order_num}`\n"
            f"🛒 *Товар:* {product_info}\n"
            f"💰 *Сумма к оплате:* {amount_stars} звезд\n"
            f"   (1 звезда = 1.4 руб, к оплате {amount_rub} руб)\n\n"
            f"📍 *Инструкция:*\n"
            f"1. Перейдите на сайт: {PAYMENT_SITE}\n"
            f"2. Укажите юзернейм получателя: `{PAYMENT_USERNAME}`\n"
            f"3. Отправьте *{amount_stars} звезд*\n\n"
        )
        await callback.message.edit_text(instruction, parse_mode="Markdown", reply_markup=back_to_catalog_keyboard())
        await callback.message.answer(
            f"✅ *После оплаты:*\n"
            f"1. Сохраните номер заказа: `{order_num}`\n"
            f"2. Сделайте скриншот подтверждения оплаты\n"
            f"3. Напишите поддержке: @your_support_username\n"
            f"4. Укажите номер заказа и приложите скриншот\n\n"
            f"⏳ *Срок выдачи:* в течение 24 часов после подтверждения оплаты\n\n"
            f"🔓 После проверки вы получите полный доступ к аккаунту.",
            parse_mode="Markdown"
        )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "support_inline")
async def support_inline_callback(callback: CallbackQuery):
    await callback.message.answer(
        "🆘 *Поддержка*\n\nСвяжитесь с нами: @your_support_username\n\n"
        "📌 *Что указать при обращении:*\n"
        "• Номер заказа\n"
        "• Сумму и способ оплаты\n"
        "• Скриншот подтверждения (для карты/звезд)\n\n"
        "⏳ *Время выдачи:* в течение 24 часов после оплаты",
        parse_mode="Markdown"
    )
    await callback.answer()

# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
