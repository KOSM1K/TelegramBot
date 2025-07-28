import telebot
import random

from chat_context import ChatContext


def register_random_member_command(context: ChatContext):
    handler_command = "random"
    handler_description = "Выбирает случайного учатника чата"

    context.add_handler_help(handler_command, handler_description)

    def get_mentions(message: telebot.types.Message):
        return [elem for elem in message.entities if elem.type == "mention"]

    @context.bot.message_handler(commands=[handler_command])
    def bot_random(message: telebot.types.Message):
        context.any_message_handler(message)

        chat_id = message.chat.id

        is_loud = "-loud" in message.text

        mentions = get_mentions(message)

        if len(mentions) > 0:
            chosen_mention = random.choice(mentions)
            response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

            context.bot.send_message(chat_id, f"Случайный выбор: {response_msg}")
            return

        chat_members = context.database.all_members_of_chat(chat_id)

        target_member = random.choice(chat_members)
        target_username = context.bot.get_chat_member(chat_id, target_member).user.username

        if is_loud:
            context.bot.send_message(chat_id,
                                     f"🎲 Случайный выбор: [{target_username}](tg://user?id={target_member})",
                                     parse_mode="Markdown")
        else:
            context.bot.send_message(
                chat_id,
                f"🎲 Случайный выбор: {target_username}"
            )
