import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7795937922

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")

bot = telebot.TeleBot(TOKEN)

bot.delete_webhook()

user_data = {}
admin_reply_target = {}
admin_action = {}


# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎛")
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🎛")
def panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Вопрос", "Баг")
    markup.row("Открытые вакансии")

    bot.send_message(message.chat.id, "Меню:", reply_markup=markup)


# =========================
# HELPER
# =========================

def step(message, s):
    data = user_data.get(message.chat.id)
    return data and data.get("step") == s


# =========================
# ВОПРОС
# =========================

@bot.message_handler(func=lambda m: m.text == "Вопрос")
def q_start(message):
    user_data[message.chat.id] = {"step": "q_nick"}
    bot.send_message(message.chat.id, "Ваш Ник:")


@bot.message_handler(func=lambda m: step(m, "q_nick"))
def q_nick(message):
    user_data[message.chat.id]["nick"] = message.text
    user_data[message.chat.id]["step"] = "q_text"
    bot.send_message(message.chat.id, "Ваш вопрос:")


@bot.message_handler(func=lambda m: step(m, "q_text"))
def q_finish(message):
    data = user_data.pop(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_{message.chat.id}"))

    bot.send_message(
        ADMIN_ID,
        f"❓ ВОПРОС\n\nНик: {data['nick']}\nВопрос: {message.text}",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "Вопрос отправлен.")


# =========================
# БАГ
# =========================

@bot.message_handler(func=lambda m: m.text == "Баг")
def b_start(message):
    user_data[message.chat.id] = {"step": "b_nick"}
    bot.send_message(message.chat.id, "Ваш Ник:")


@bot.message_handler(func=lambda m: step(m, "b_nick"))
def b_nick(message):
    user_data[message.chat.id]["nick"] = message.text
    user_data[message.chat.id]["step"] = "b_bug"
    bot.send_message(message.chat.id, "Опишите баг:")


@bot.message_handler(func=lambda m: step(m, "b_bug"))
def b_finish(message):
    data = user_data.pop(message.chat.id)

    bot.send_message(
        ADMIN_ID,
        f"🐞 БАГ\n\nНик: {data['nick']}\nБаг: {message.text}"
    )

    bot.send_message(message.chat.id, "Баг отправлен.")


# =========================
# ВАКАНСИИ
# =========================

@bot.message_handler(func=lambda m: m.text == "Открытые вакансии")
def jobs(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Медиа", url="https://docs.google.com/forms/d/1ZUh1SNLY0n4PeevHKWy6SeoTBDP-nTJwTV2f4VjcwOk/viewform"))
    markup.add(types.InlineKeyboardButton("Стажер", url="https://docs.google.com/forms/d/1sqtfB4KQL9yE_PXBtPdKTpoIc7VQqrYHk4NbmkfzNFQ/viewform"))

    bot.send_message(
        message.chat.id,
        "Открытые вакансии:\n\n• Медиа\n• Стажер",
        reply_markup=markup
    )


# =========================
# ОТВЕТ АДМИНА
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def reply(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    admin_reply_target[ADMIN_ID] = user_id

    msg = bot.send_message(ADMIN_ID, "Введите ответ:")
    bot.register_next_step_handler(msg, send_reply)


def send_reply(message):
    user_id = admin_reply_target.get(message.chat.id)

    if user_id:
        bot.send_message(user_id, f"📩 Ответ: {message.text}")

    bot.send_message(ADMIN_ID, "Отправлено.")


# =========================
# RUN
# =========================

bot.polling(none_stop=True, interval=0)
