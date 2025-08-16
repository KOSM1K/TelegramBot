import subprocess
import telebot
import time
import datetime

from chat_context import ChatContext


def register_update_command(context: ChatContext):
    handler_command = "update"
    handler_description = "Обновить ботика с гита"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def bot_update(message: telebot.types.Message):
        context.any_message_handler(message)

        subprocess.Popen(
        ["systemd-run ./linux_service_update.sh"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

        
