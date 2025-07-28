import telebot
import random
from chat_context import ChatContext

# Осуждаю максимально
rage_phrases = [
    "иди нахуй",
    "НАХУЙ ИДИ! И-Д-И Н-А-Х-У-Й!!!",
    "ооо, блять, пидор проснулся",
    "да как же ты меня заебал",
    "сосал? да не отвечай, сразу вижу, что да",
    "да поебать мне!",
    "твое место у параши.",
    "хорошо тебе с хуем в жопе живется?",
    "да когда ж ты ебало то завалишь...",
    "ЕБАЛО СВОЕ ОФФНИ, ЧУРКА!"
]


def register_rage_command(context: ChatContext):
    handler_command = "fuck_you"
    handler_description = "Выбирает случайное оскорбление из списка"

    context.add_handler_help(handler_command, handler_description)

    @context.bot.message_handler(commands=[handler_command])
    def rage(message: telebot.types.Message):
        context.any_message_handler(message)

        rage_phrase = random.choice(rage_phrases)

        if message.reply_to_message:
            original_msg = message.reply_to_message
            context.bot.reply_to(original_msg, rage_phrase)
        else:
            context.bot.send_message(message.chat.id, rage_phrase)

        if not message.forward_from:
            context.bot.delete_message(message.chat.id, message.id)
