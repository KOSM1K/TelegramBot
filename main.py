import telebot
# from transformers import pipeline
import random
from hidden import token

TOKEN = token
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения пользователей чата (chat_id -> set(user_id))
chat_members = {}

# Команда /rand выбирает случайного участника
@bot.message_handler(commands=['rand'])
def random_user(message):
    chat_id = message.chat.id

    if chat_id in chat_members and chat_members[chat_id]:
        chosen_one = random.choice(list(chat_members[chat_id]))
        bot.send_message(chat_id, f"🎲 Случайный выбор: [{bot.get_chat_member(chat_id, chosen_one).user.username}](tg://user?id={chosen_one})", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "Не могу выбрать никого, недостаточно данных 🫤")


# Запоминаем участников, когда они что-то пишут
@bot.message_handler()
def save_users(message):
    print("someone typing")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in chat_members:
        chat_members[chat_id] = set()

    # Добавляем пользователя, если это не бот
    if not message.from_user.is_bot:
        chat_members[chat_id].add(user_id)

if __name__ == "__main__":
    bot.infinity_polling()