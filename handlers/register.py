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

        if message.reply_to_message:
            mention = message.reply_to_message.from_user
        else:
            mention = message.from_user

        chat_id = message.chat.id

        if not mention.is_bot:
            if mention.id not in context.database.all_members_of_chat(chat_id):
                context.database.add_member(mention.id, chat_id)

                context.bot.reply_to(message, f"Участник {mention.username} добавлен")
                return
            else:
                context.bot.reply_to(message, f"Участник {mention.username} уже добавлен")
        else:
            context.bot.reply_to(message, f"Участник {mention.username} - бот, его нельзя зарегистрировать")
        
