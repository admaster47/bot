import telebot
import random
import time
import os

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN") or "ТВОЙ_ТОКЕН_СЮДА"

# Кошелёк для USDT (замени на свой)
USDT_WALLET = "TQYkqKxpK8nMpJ5Qz5g5LxKqZvHp3WYQyA"

# Банковские реквизиты (замени на свои)
BANK_NAME = "Т-Банк"
BANK_CARD = "1234 5678 9012 3456"
BANK_HOLDER = "Иванов Иван Иванович"

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(TOKEN)

# Хранилище заказов (в реальном проекте используй БД)
orders = {}

# ========== ГЕНЕРАТОРЫ ==========
def generate_order_id():
    return f"ORD{int(time.time())}{random.randint(10, 99)}"

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📦 Каталог", "💰 Мои покупки")
    keyboard.row("❓ Помощь")
    return keyboard

def catalog_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Яндекс Сплит", "💼 Корпоративный счет")
    keyboard.row("🚗 Яндекс Каршеринг")
    keyboard.row("🔙 Назад в главное меню")
    return keyboard

def split_balances_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    balances = [30000, 50000, 70000, 100000, 150000]
    for balance in balances:
        price = int(balance * 0.05)
        keyboard.add(telebot.types.InlineKeyboardButton(
            text=f"{balance} ₽ (цена {price} ₽)",
            callback_data=f"split_{balance}"
        ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_catalog"
    ))
    return keyboard

def payment_keyboard(order_id, price):
    """Клавиатура выбора способа оплаты"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🪙 Оплата криптой (USDT)",
        callback_data=f"pay_crypto_{order_id}_{price}"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="💳 Оплата картой (₽)",
        callback_data=f"pay_card_{order_id}_{price}"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_catalog"
    ))
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🖐️ *Добро пожаловать в магазин!*\n\n"
        "Мы продаём:\n"
        "✅ *Прогретые аккаунты Яндекс Сплит* (баланс 30-150к, цена 5%)\n"
        "✅ *Корпоративные счета Яндекса* (5000 ₽)\n"
        "✅ *Аккаунты Яндекс Каршеринга* (1500 ₽)\n\n"
        "Все аккаунты прогреты и готовы к работе!\n\n"
        "📦 *Каталог*\n"
        "💰 *Мои покупки*\n"
        "❓ *Помощь*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📦 Каталог")
def show_catalog(message):
    bot.send_message(
        message.chat.id,
        "📦 *Выбери категорию:*",
        parse_mode="Markdown",
        reply_markup=catalog_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🚀 Яндекс Сплит")
def show_split_balances(message):
    text = (
        "🚀 *Аккаунты Яндекс Сплит*\n\n"
        "Готовые рекламные кабинеты с уже залитым балансом.\n"
        "✅ Прогретые\n"
        "✅ Готовы к работе\n\n"
        "💰 *Цена: 5% от баланса*\n\n"
        "Выбери нужный баланс:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=split_balances_keyboard())

@bot.message_handler(func=lambda message: message.text == "💼 Корпоративный счет")
def show_corporate(message):
    text = (
        "💼 *Корпоративный счет Яндекса*\n\n"
        "✅ Полностью верифицированный\n"
        "✅ Высокие лимиты\n"
        "✅ Прогретый и готов к работе\n\n"
        "💰 *Цена: 5000 ₽*"
    )
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="💼 Купить за 5000 ₽",
        callback_data="corporate"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_catalog"
    ))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🚗 Яндекс Каршеринг")
def show_carsharing(message):
    text = (
        "🚗 *Аккаунт Яндекс Каршеринга*\n\n"
        "✅ Прогретый аккаунт\n"
        "✅ Готов к использованию\n\n"
        "💰 *Цена: 1500 ₽*"
    )
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🚗 Купить за 1500 ₽",
        callback_data="carsharing"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_catalog"
    ))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "💰 Мои покупки")
def show_purchases(message):
    bot.send_message(
        message.chat.id,
        "📦 *История покупок*\n\nПока пусто. После оплаты товары появятся здесь.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def show_help(message):
    help_text = (
        "❓ *Помощь*\n\n"
        "📦 *Как купить:*\n"
        "1. Выбери товар в каталоге\n"
        "2. Оплати удобным способом\n"
        "3. Напиши в поддержку чек\n"
        "4. Получи аккаунт в течение 24 часов\n\n"
        "📩 *Поддержка:* @support_shop\n"
        "⏱ Время ответа: до 15 минут"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
def back_to_main(message):
    send_welcome(message)

# ========== ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)
    
    data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Назад в каталог
    if data == "back_to_catalog":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📦 *Выбери категорию:*",
            parse_mode="Markdown",
            reply_markup=catalog_keyboard()
        )
        return
    
    # Выбор баланса Сплита
    if data.startswith("split_"):
        balance = int(data.split("_")[1])
        price = int(balance * 0.05)
        order_id = generate_order_id()
        
        orders[order_id] = {
            "user_id": call.from_user.id,
            "product": f"Яндекс Сплит ({balance} ₽)",
            "price": price,
            "status": "pending"
        }
        
        text = (
            f"✅ *Товар:* Яндекс Сплит ({balance} ₽)\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"💰 *Сумма:* {price} ₽\n\n"
            f"Выбери способ оплаты:"
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, price)
        )
        return
    
    # Корпоративный счёт
    if data == "corporate":
        order_id = generate_order_id()
        price = 5000
        
        orders[order_id] = {
            "user_id": call.from_user.id,
            "product": "Корпоративный счет Яндекса",
            "price": price,
            "status": "pending"
        }
        
        text = (
            f"✅ *Товар:* Корпоративный счет Яндекса\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"💰 *Сумма:* {price} ₽\n\n"
            f"Выбери способ оплаты:"
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, price)
        )
        return
    
    # Каршеринг
    if data == "carsharing":
        order_id = generate_order_id()
        price = 1500
        
        orders[order_id] = {
            "user_id": call.from_user.id,
            "product": "Аккаунт Яндекс Каршеринга",
            "price": price,
            "status": "pending"
        }
        
        text = (
            f"✅ *Товар:* Аккаунт Яндекс Каршеринга\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"💰 *Сумма:* {price} ₽\n\n"
            f"Выбери способ оплаты:"
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, price)
        )
        return
    
    # ===== ОПЛАТА КРИПТОЙ (ТОЛЬКО ТЕКСТ, БЕЗ ССЫЛОК) =====
    if data.startswith("pay_crypto_"):
        parts = data.split("_")
        order_id = parts[2]
        price = parts[3]
        
        text = (
            f"🪙 *Оплата криптовалютой USDT*\n\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"💰 *Сумма к оплате:* {price} USDT\n\n"
            f"📤 *Реквизиты для перевода:*\n"
            f"`{USDT_WALLET}`\n\n"
            f"🌐 *Сеть:* TRC-20 (USDT)\n\n"
            f"📌 *Инструкция:*\n"
            f"1. Открой свой криптокошелек (Binance, Bybit, OKX и т.д.)\n"
            f"2. Выбери перевод USDT в сети TRC-20\n"
            f"3. Введи указанный выше кошелек\n"
            f"4. Укажи сумму {price} USDT\n"
            f"5. Отправь перевод\n\n"
            f"✅ *После оплаты:*\n"
            f"Сделай скриншот чека и отправь его в поддержку:\n"
            f"📩 @support_shop\n\n"
            f"⏰ Аккаунт будет выдан в течение 24 часов после подтверждения оплаты."
        )
        
        # Простая кнопка "Назад" без ссылок
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(
            text="🔙 Назад в каталог",
            callback_data="back_to_catalog"
        ))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    # ===== ОПЛАТА КАРТОЙ (ТОЛЬКО ТЕКСТ, БЕЗ ССЫЛОК) =====
    if data.startswith("pay_card_"):
        parts = data.split("_")
        order_id = parts[2]
        price = int(parts[3])
        
        text = (
            f"💳 *Оплата банковской картой*\n\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"💰 *Сумма к оплате:* {price} ₽\n\n"
            f"📤 *Реквизиты для перевода:*\n"
            f"🏦 *Банк:* {BANK_NAME}\n"
            f"💳 *Номер карты:* `{BANK_CARD}`\n"
            f"👤 *Получатель:* {BANK_HOLDER}\n\n"
            f"📌 *Инструкция:*\n"
            f"1. Открой приложение своего банка\n"
            f"2. Выбери перевод по номеру карты\n"
            f"3. Введи указанный выше номер карты\n"
            f"4. Укажи сумму {price} ₽\n"
            f"5. Отправь перевод\n\n"
            f"✅ *После оплаты:*\n"
            f"Сделай скриншот чека и отправь его в поддержку:\n"
            f"📩 @support_shop\n\n"
            f"⏰ Аккаунт будет выдан в течение 24 часов после подтверждения оплаты."
        )
        
        # Простая кнопка "Назад" без ссылок
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(
            text="🔙 Назад в каталог",
            callback_data="back_to_catalog"
        ))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("✅ Бот запущен!")
    bot.infinity_polling()
