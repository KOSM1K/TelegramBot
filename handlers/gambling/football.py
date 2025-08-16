import telebot

from chat_context import ChatContext
from handlers.gambling.dice_emoji import dice_emoji


def register_gambling_football_command(context: ChatContext):
    handler_command = "football"
    handler_description = "депает в футбик"

    context.add_handler_help(handler_command, handler_description)

    def get_slots_score(dice: telebot.types.Dice):
        dice_value = dice.value

        print(dice)
        print(dice_value)

        if dice_value == 3:
            return 2, True

        if dice_value in (4, 5):
            return 1.5, True

        return 0, False

    @context.bot.message_handler(commands=[handler_command])
    def slots(message: telebot.types.Message):
        dice_emoji(context, message, "⚽", handler_command, get_slots_score)
