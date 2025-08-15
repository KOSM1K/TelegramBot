import telebot
import time
import datetime

from chat_context import ChatContext


def register_register_command(context: ChatContext):
    handler_command = "register"
    handler_description = "Зарегать участника"

    context.add_handler_help(handler_command, handler_description)

    def get_mentions(message: telebot.types.Message):
        return [elem for elem in message.entities if elem.type == "mention"]

    @context.bot.message_handler(commands=[handler_command])
    def bot_uptime(message: telebot.types.Message):
        context.any_message_handler(message)

        if not message.reply_to_message:
            context.bot.reply_to(message, "Отправьте в ответ на сообщения участника для добавления")
            return

        chat_id = message.chat.id
        mention = message.reply_to_message.from_user

        if mention.id not in context.database.all_members_of_chat(chat_id):
            context.database.add_member(mention.id, chat_id)

            context.bot.reply_to(message, f"Участник {mention.username} добавлен")
            return

        context.bot.reply_to(message, f"Участник {mention.username} уже добавлен")
