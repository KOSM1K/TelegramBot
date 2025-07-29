import telebot

from chat_context import ChatContext


def register_exec_command(context: ChatContext):
    handler_command = "exec"
    handler_description = "Запускает программы"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def bot_exec(message: telebot.types.Message):
        context.any_message_handler(message)

        context.bot.reply_to(message, "Ну игра же ещё в стадии разработки!")