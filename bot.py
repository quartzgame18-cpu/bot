import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7795937922

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")

bot = telebot.TeleBot(TOKEN)

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
    markup.row("Жалоба на игрока")

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
    bot.send_message(message.chat.id, "Баг:")


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

    markup.add(types.InlineKeyboardButton("Медиа", url="https://docs.google.com/..."))
    markup.add(types.InlineKeyboardButton("Стажер", url="https://docs.google.com/..."))

    bot.send_message(
        message.chat.id,
        "Открытые вакансии:\n\n• Медиа\n• Стажер",
        reply_markup=markup
    )


# =========================
# ЖАЛОБА
# =========================

@bot.message_handler(func=lambda m: m.text == "Жалоба на игрока")
def c_start(message):
    user_data[message.chat.id] = {"step": "c_nick"}
    bot.send_message(message.chat.id, "Ваш Ник:")


@bot.message_handler(func=lambda m: step(m, "c_nick"))
def c_nick(message):
    user_data[message.chat.id]["your_nick"] = message.text
    user_data[message.chat.id]["step"] = "c_player"
    bot.send_message(message.chat.id, "Ник игрока:")


@bot.message_handler(func=lambda m: step(m, "c_player"))
def c_player(message):
    user_data[message.chat.id]["player"] = message.text
    user_data[message.chat.id]["step"] = "c_reason"
    bot.send_message(message.chat.id, "Причина:")


@bot.message_handler(func=lambda m: step(m, "c_reason"))
def c_reason(message):
    user_data[message.chat.id]["reason"] = message.text
    user_data[message.chat.id]["step"] = "c_proof"
    bot.send_message(message.chat.id, "Отправьте доказательства (фото/видео/текст):")


@bot.message_handler(content_types=['photo', 'video', 'text'])
def c_proof(message):
    data = user_data.get(message.chat.id)

    if not data or data.get("step") != "c_proof":
        return

    media = None
    media_type = None

    if message.photo:
        media = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        media = message.video.file_id
        media_type = "video"
    else:
        media = message.text
        media_type = "text"

    text = f"""
🚨 ЖАЛОБА

Ваш Ник: {data['your_nick']}
Игрок: {data['player']}
Причина: {data['reason']}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Принять", callback_data=f"acc_{message.chat.id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"rej_{message.chat.id}")
    )

    bot.send_message(ADMIN_ID, text, reply_markup=markup)

    if media_type == "photo":
        bot.send_photo(ADMIN_ID, media)
    elif media_type == "video":
        bot.send_video(ADMIN_ID, media)
    else:
        bot.send_message(ADMIN_ID, f"Доказательства: {media}")

    bot.send_message(message.chat.id, "Жалоба отправлена.")

    user_data.pop(message.chat.id, None)


# =========================
# АДМИН ВОПРОС ОТВЕТ
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def reply(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    admin_reply_target[ADMIN_ID] = user_id

    msg = bot.send_message(ADMIN_ID, "Ответ:")
    bot.register_next_step_handler(msg, send_reply)


def send_reply(message):
    user_id = admin_reply_target.get(message.chat.id)

    if user_id:
        bot.send_message(user_id, f"📩 Ответ: {message.text}")

    bot.send_message(ADMIN_ID, "Отправлено.")


# =========================
# ПРИНЯТЬ / ОТКЛОНИТЬ
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("acc_"))
def acc(call):
    user_id = int(call.data.split("_")[1])
    admin_action[ADMIN_ID] = user_id

    msg = bot.send_message(ADMIN_ID, "Наказание:")
    bot.register_next_step_handler(msg, send_acc)


def send_acc(message):
    user_id = admin_action.get(message.chat.id)
    bot.send_message(user_id, f"✅ Жалоба принята\n\n{message.text}")
    bot.send_message(ADMIN_ID, "Готово.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_"))
def rej(call):
    user_id = int(call.data.split("_")[1])
    admin_action[ADMIN_ID] = user_id

    msg = bot.send_message(ADMIN_ID, "Причина отклонения:")
    bot.register_next_step_handler(msg, send_rej)


def send_rej(message):
    user_id = admin_action.get(message.chat.id)
    bot.send_message(user_id, f"❌ Жалоба отклонена\n\n{message.text}")
    bot.send_message(ADMIN_ID, "Готово.")


# =========================
# RUN
# =========================

bot.polling(none_stop=True)
