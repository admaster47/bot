import telebot
import random
import time
import os

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN") or "ТВОЙ_ТОКЕН_СЮДА"

# Кошелёк для USDT (замени на свой)
USDT_WALLET = "TQYkqKxpK8nMpJ5Qz5g5LxKqZvHp3WYQyA"

# Банковская карта (замени на свою)
BANK_CARD = "1234 5678 9012 3456"

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(TOKEN)

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📦 Каталог")
    keyboard.row("💰 Мои покупки", "❓ Помощь")
    return keyboard

def catalog_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Яндекс Сплит", "💼 Корпоративный счет")
    keyboard.row("🚗 Яндекс Каршеринг")
    keyboard.row("🔙 Назад в главное меню")
    return keyboard

def split_balances_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("30 000 ₽", "50 000 ₽", "70 000 ₽")
    keyboard.row("100 000 ₽", "150 000 ₽")
    keyboard.row("🔙 Назад в каталог")
    return keyboard

# ========== ОБРАБОТЧИКИ ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 *Привет! Я бот для покупки аккаунтов.*\n\n"
        "У нас вы можете купить:\n"
        "✅ *Аккаунты Яндекс Сплит* — от 30 000₽ до 150 000₽ (цена 5% от баланса)\n"
        "✅ *Корпоративные счета Яндекса* — 5 000₽\n"
        "✅ *Аккаунты Яндекс Каршеринга* — 1 500₽\n\n"
        "Все аккаунты *прогретые* и готовы к работе!\n\n"
        "👇 *Нажмите «Каталог» чтобы выбрать товар*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📦 Каталог")
def show_catalog(message):
    bot.send_message(
        message.chat.id,
        "📦 *Выберите категорию товаров:*",
        parse_mode="Markdown",
        reply_markup=catalog_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🚀 Яндекс Сплит")
def show_split_balances(message):
    text = (
        "🚀 *Аккаунты Яндекс Сплит*\n\n"
        "💰 *Цена: 5% от баланса*\n\n"
        "Выберите нужный баланс:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=split_balances_keyboard())

@bot.message_handler(func=lambda message: message.text in ["30 000 ₽", "50 000 ₽", "70 000 ₽", "100 000 ₽", "150 000 ₽"])
def handle_split_purchase(message):
    balance_text = message.text.replace(" ₽", "").replace(" ", "")
    balance = int(balance_text)
    price = int(balance * 0.05)
    
    order_id = f"ORD{int(time.time())}{random.randint(10, 99)}"
    
    text = (
        f"✅ *Вы выбрали:* Яндекс Сплит ({balance} ₽)\n"
        f"🧾 *Номер заказа:* `{order_id}`\n"
        f"💰 *Сумма к оплате:* {price} ₽\n\n"
        f"👇 *Выберите способ оплаты:*"
    )
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🪙 Оплатить криптой (USDT)", "💳 Оплатить картой")
    keyboard.row("🔙 Назад в каталог")
    
    # Сохраняем заказ
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "💼 Корпоративный счет")
def handle_corporate(message):
    order_id = f"ORD{int(time.time())}{random.randint(10, 99)}"
    price = 5000
    
    text = (
        f"✅ *Вы выбрали:* Корпоративный счет Яндекса\n"
        f"🧾 *Номер заказа:* `{order_id}`\n"
        f"💰 *Сумма к оплате:* {price} ₽\n\n"
        f"👇 *Выберите способ оплаты:*"
    )
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🪙 Оплатить криптой (USDT)", "💳 Оплатить картой")
    keyboard.row("🔙 Назад в каталог")
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🚗 Яндекс Каршеринг")
def handle_carsharing(message):
    order_id = f"ORD{int(time.time())}{random.randint(10, 99)}"
    price = 1500
    
    text = (
        f"✅ *Вы выбрали:* Аккаунт Яндекс Каршеринга\n"
        f"🧾 *Номер заказа:* `{order_id}`\n"
        f"💰 *Сумма к оплате:* {price} ₽\n\n"
        f"👇 *Выберите способ оплаты:*"
    )
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🪙 Оплатить криптой (USDT)", "💳 Оплатить картой")
    keyboard.row("🔙 Назад в каталог")
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🪙 Оплатить криптой (USDT)")
def pay_crypto(message):
    # Нужно получить последний заказ пользователя
    # Для простоты используем статическую сумму
    text = (
        "🪙 *Оплата криптовалютой USDT*\n\n"
        f"📤 *Переведите оплату на адрес:*\n"
        f"`{USDT_WALLET}`\n\n"
        f"💰 *Сеть:* TRC-20\n\n"
        f"✅ *После оплаты:*\n"
        f"В течение 24 часов вам придут данные от аккаунта.\n\n"
        f"📩 *По вопросам:* @support_shop"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💳 Оплатить картой")
def pay_card(message):
    text = (
        "💳 *Оплата банковской картой*\n\n"
        f"📤 *Переведите оплату на карту:*\n"
        f"`{BANK_CARD}`\n\n"
        f"✅ *После оплаты:*\n"
        f"В течение 24 часов вам придут данные от аккаунта.\n\n"
        f"📩 *По вопросам:* @support_shop"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в каталог")
def back_to_catalog(message):
    show_catalog(message)

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
def back_to_main(message):
    send_welcome(message)

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
        "1️⃣ Выберите товар в каталоге\n"
        "2️⃣ Нажмите на нужный баланс или товар\n"
        "3️⃣ Выберите способ оплаты\n"
        "4️⃣ Переведите деньги по реквизитам\n"
        "5️⃣ Данные аккаунта придут в течение 24 часов\n\n"
        "📩 *Поддержка:* @support_shop\n"
        "⏱ *Время ответа:* до 15 минут"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен!")
    bot.infinity_polling()
