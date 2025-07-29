import random

import telebot
import random
import shlex

from chat_context import ChatContext


def register_choose_from_command(context: ChatContext):
    handler_command = "choose"
    handler_description = "Выбирает из списка вариантов"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def handler(message: telebot.types.Message):
        args_raw = message.text.partition(' ')[2]

        try:
            args = shlex.split(args_raw)
        except ValueError as e:
            context.bot.reply_to(message, f"Ошибка при разборе аргументов: {e}")
            return

        if not args:
            context.bot.reply_to(message, "Вы не указали варианты.")
            return

        chosen = random.choice(args)
        context.bot.reply_to(message, f"Я выбираю: {chosen}")
