import telebot

from chat_context import ChatContext
from handlers.gambling.dice_emoji import dice_emoji


def register_gambling_slots_command(context: ChatContext):
    handler_command = "slots"
    handler_description = "депает в слотики"

    context.add_handler_help(handler_command, handler_description)

    def get_slots_score(dice: telebot.types.Dice):
        dice_value = dice.value

        print(dice)
        print(dice_value)

        # https://gist.github.com/Chase22/300bad79154ffd5d8fbf0aedd5ddc4d4
        if dice_value == 64:
            return 20, True  # 7 x3
        elif dice_value == 43:
            return 5, True  # lemon x3
        elif dice_value == 22:
            return 3, True  # grape x3
        elif dice_value == 1:
            return 2, True  # bar x3
        elif dice_value in (16, 32, 48):
            return 1.5, True  # first two seven
        elif dice_value in (16, 32, 48):
            return 1.5, True  # first two sever
        elif dice_value in (44, 42, 41, 11, 47):
            return 1.3, True
        elif dice_value in (17, 27, 30, 33, 35, 38, 39):
            return 1.2, True
        else:
            return 0, False

    @context.bot.message_handler(commands=[handler_command])
    def slots(message: telebot.types.Message):
        dice_emoji(context, message, "🎰", handler_command, get_slots_score)
