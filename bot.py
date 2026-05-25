import telebot
from telebot import types

TOKEN = ""
ADMIN_ID = 

bot = telebot.TeleBot(TOKEN)

user_data = {}
admin_reply_target = {}


# ======================
# START
# ======================

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎛")
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🎛")
def panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Вопрос")
    markup.row("Открытые вакансии")
    markup.row("Баг")
    bot.send_message(message.chat.id, "Выберите пункт:", reply_markup=markup)


# ======================
# ВОПРОС
# ======================

@bot.message_handler(func=lambda m: m.text == "Вопрос")
def question_start(message):
    user_data[message.chat.id] = {"step": "nick"}
    bot.send_message(message.chat.id, "Ваш Ник:")


@bot.message_handler(func=lambda m: message_step(m, "nick"))
def question_nick(message):
    user_data[message.chat.id]["nick"] = message.text
    user_data[message.chat.id]["step"] = "question"
    bot.send_message(message.chat.id, "Ваш вопрос:")


@bot.message_handler(func=lambda m: message_step(m, "question"))
def question_finish(message):
    data = user_data[message.chat.id]

    text = f"""❓ Новый вопрос
Ник: {data['nick']}
Вопрос: {message.text}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "Ответить",
        callback_data=f"reply_{message.chat.id}"
    ))

    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_message(message.chat.id, "Вопрос отправлен руководству.")

    user_data.pop(message.chat.id)


# ======================
# БАГ
# ======================

@bot.message_handler(func=lambda m: m.text == "Баг")
def bug_start(message):
    user_data[message.chat.id] = {"step": "b_nick"}
    bot.send_message(message.chat.id, "Ваш Ник:")


@bot.message_handler(func=lambda m: message_step(m, "b_nick"))
def bug_nick(message):
    user_data[message.chat.id]["nick"] = message.text
    user_data[message.chat.id]["step"] = "bug"
    bot.send_message(message.chat.id, "Обнаруженный Баг:")


@bot.message_handler(func=lambda m: message_step(m, "bug"))
def bug_text(message):
    user_data[message.chat.id]["bug"] = message.text
    user_data[message.chat.id]["step"] = "how"
    bot.send_message(message.chat.id, "Как вы его обнаружили:")


@bot.message_handler(func=lambda m: message_step(m, "how"))
def bug_finish(message):
    data = user_data[message.chat.id]

    text = f"""🐞 Новый баг
Ник: {data['nick']}
Баг: {data['bug']}
Как обнаружил: {message.text}
"""

    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "Баг передан тестировщикам.")

    user_data.pop(message.chat.id)


# ======================
# ВАКАНСИИ
# ======================

@bot.message_handler(func=lambda m: m.text == "Открытые вакансии")
def jobs(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подать", callback_data="apply"))

    bot.send_message(
        message.chat.id,
        "Открытые вакансии:\n\n• Стажер\n• Медиа",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "apply")
def apply(call):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton(
        "Медиа",
        url="https://docs.google.com/forms/d/1ZUh1SNLY0n4PeevHKWy6SeoTBDP-nTJwTV2f4VjcwOk/viewform"
    ))

    markup.add(types.InlineKeyboardButton(
        "Стажер",
        url="https://docs.google.com/forms/d/1sqtfB4KQL9yE_PXBtPdKTpoIc7VQqrYHk4NbmkfzNFQ/viewform"
    ))

    bot.send_message(call.message.chat.id, "Выберите вакансию:", reply_markup=markup)


# ======================
# ОТВЕТ АДМИНА
# ======================

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def reply(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    admin_reply_target[call.from_user.id] = user_id

    msg = bot.send_message(ADMIN_ID, "Введите ответ игроку:")
    bot.register_next_step_handler(msg, send_reply)


def send_reply(message):
    user_id = admin_reply_target.get(message.chat.id)

    if user_id:
        bot.send_message(user_id, f"📩 Ответ администрации:\n\n{message.text}")
        bot.send_message(message.chat.id, "Ответ отправлен.")


# ======================
# helper
# ======================

def message_step(message, step):
    data = user_data.get(message.chat.id)
    return data and data.get("step") == step


bot.polling(none_stop=True)