import telebot
import time
import datetime

from chat_context import ChatContext


def register_uptime_command(context: ChatContext):
    handler_command = "uptime"
    handler_description = "Как долго я работал?"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def bot_uptime(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id
        duration = time.time() - context.start_time
        context.bot.send_message(chat_id, f"Я запущен уже {
            datetime.timedelta(seconds=duration)
        }")
        print("Uptime!")
