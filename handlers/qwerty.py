import telebot

from chat_context import ChatContext

eng_to_rus = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,.`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>~",
    "йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ"
)


def register_qwerty_command(context: ChatContext):
    handler_command = "qw"
    handler_description = "Переводит текст из qwerty в йцукен"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def qwerty_cmd(message: telebot.types.Message):
        context.any_message_handler(message)

        if message.reply_to_message:
            original_msg = message.reply_to_message
            text = original_msg.text
        else:
            context.bot.reply_to(message, "Это не ответ на сообщение.")
            return

        converted = text.translate(eng_to_rus)
        context.bot.reply_to(message, converted)
