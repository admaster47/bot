import telebot
import random
import time
TOKEN = "8783926681:AAEQrtO5NAzTLHYbhm7SOiFK2e0ZqOicIYY" 
USDT_WALLET = "TMG81Fpuo82pt4f7YDS9uTmj4vvYht6dNP"

# Сайт для оплаты звёздами
STAR_PAYMENT_URL = "https://split.tg"

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(TOKEN)

# ========== КЛАВИАТУРЫ ==========

def main_keyboard():
    """Главная клавиатура"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📦 Каталог", "💰 Мои покупки")
    keyboard.row("❓ Помощь")
    return keyboard

def catalog_keyboard():
    """Клавиатура каталога"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Яндекс Сплит", "💼 Корпоративный счет")
    keyboard.row("🚗 Яндекс Каршеринг")
    keyboard.row("🔙 Назад в главное меню")
    return keyboard

def split_balances_keyboard():
    """Клавиатура с выбором баланса Сплита"""
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
    """Клавиатура выбора оплаты"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🪙 Оплата криптой (USDT)",
        callback_data=f"pay_crypto_{order_id}_{price}"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="💳 Оплата картой (Звёзды)",
        callback_data=f"pay_card_{order_id}_{price}"
    ))
    keyboard.add(telebot.types.InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_catalog"
    ))
    return keyboard

# ========== ГЕНЕРАТОРЫ ==========

def generate_order_id():
    """Генерация номера заказа"""
    return f"ORD{int(time.time())}{random.randint(10, 99)}"

# ========== КОМАНДЫ БОТА ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие с главным меню"""
    welcome_text = (
        "🖐️ *Добро пожаловать в магазин!*\n\n"
        "Мы продаём:\n"
        "✅ *Прогретые аккаунты Яндекс Сплит* (баланс 30-150к, цена 5%)\n"
        "✅ *Корпоративные счета Яндекса* (5000 ₽)\n"
        "✅ *Аккаунты Яндекс Каршеринга* (1500 ₽)\n\n"
        "📦 *Каталог*\n"
        "💰 *Мои покупки*\n"
        "❓ *Помощь*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📦 Каталог")
def show_catalog(message):
    bot.send_message(message.chat.id, "📦 *Выбери категорию:*", parse_mode="Markdown", reply_markup=catalog_keyboard())

@bot.message_handler(func=lambda message: message.text == "🚀 Яндекс Сплит")
def show_split(message):
    text = "🚀 *Аккаунты Яндекс Сплит*\n\n💰 Цена: 5% от баланса\n\nВыбери баланс:"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=split_balances_keyboard())

@bot.message_handler(func=lambda message: message.text == "💼 Корпоративный счет")
def show_corporate(message):
    text = "💼 *Корпоративный счет Яндекса*\n✅ Верифицирован\n✅ Прогрет\n💰 Цена: 5000 ₽"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💼 Купить за 5000 ₽", callback_data="corporate"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_catalog"))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🚗 Яндекс Каршеринг")
def show_carsharing(message):
    text = "🚗 *Аккаунт Яндекс Каршеринга*\n✅ Прогретый\n💰 Цена: 1500 ₽"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🚗 Купить за 1500 ₽", callback_data="carsharing"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_catalog"))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "💰 Мои покупки")
def show_purchases(message):
    bot.send_message(message.chat.id, "📦 *История покупок*\nПока пусто.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def show_help(message):
    help_text = "❓ *Помощь*\n\n📩 Поддержка: @support_shop\n⏱ Время ответа: до 15 минут"
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
def back_to_main(message):
    send_welcome(message)

# ========== ОБРАБОТКА КНОПОК ==========

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # Назад в каталог
    if call.data == "back_to_catalog":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📦 *Выбери категорию:*",
            parse_mode="Markdown",
            reply_markup=catalog_keyboard()
        )
        return
    
    # Выбор Сплита
    if call.data.startswith("split_"):
        balance = int(call.data.split("_")[1])
        price = int(balance * 0.05)
        order_id = generate_order_id()
        text = f"✅ *Товар:* Яндекс Сплит ({balance} ₽)\n🧾 *Заказ:* `{order_id}`\n💰 *Сумма:* {price} ₽\n\nВыбери способ оплаты:"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, price)
        )
        return
    
    # Корпоративный счёт
    if call.data == "corporate":
        order_id = generate_order_id()
        text = f"✅ *Товар:* Корпоративный счет\n🧾 *Заказ:* `{order_id}`\n💰 *Сумма:* 5000 ₽\n\nВыбери способ оплаты:"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, 5000)
        )
        return
    
    # Каршеринг
    if call.data == "carsharing":
        order_id = generate_order_id()
        text = f"✅ *Товар:* Каршеринг\n🧾 *Заказ:* `{order_id}`\n💰 *Сумма:* 1500 ₽\n\nВыбери способ оплаты:"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=payment_keyboard(order_id, 1500)
        )
        return
    
    # Оплата криптой
    if call.data.startswith("pay_crypto_"):
        parts = call.data.split("_")
        order_id = parts[2]
        price = parts[3]
        text = (
            f"🪙 *Оплата USDT*\n\n🧾 Заказ: `{order_id}`\n💰 Сумма: {price} USDT\n\n"
            f"1️⃣ Переведи *{price} USDT* на кошелёк:\n`{USDT_WALLET}`\n\n"
            f"2️⃣ После перевода напиши в поддержку\n\n📩 @support_shop"
        )
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("📩 Написать в поддержку", url="https://t.me/support_shop"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    # Оплата картой
    if call.data.startswith("pay_card_"):
        parts = call.data.split("_")
        order_id = parts[2]
        price = int(parts[3])
        stars = int(price / 0.75)
        text = (
            f"💳 *Оплата картой (Звёзды)*\n\n🧾 Заказ: `{order_id}`\n💰 Сумма: {price} ₽\n⭐ Нужно звёзд: {stars}\n\n"
            f"1️⃣ Перейди по ссылке: {STAR_PAYMENT_URL}\n"
            f"2️⃣ Оплати {stars} звёзд\n"
            f"3️⃣ Напиши в поддержку\n\n📩 @support_shop"
        )
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("📩 Написать в поддержку", url="https://t.me/support_shop"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен!")
    bot.infinity_polling()
