import telebot

from chat_context import ChatContext


def register_new_member_handler(context: ChatContext):
    @context.bot.message_handler(content_types=['new_chat_members'])
    def handle_new_member(message: telebot.types.Message):
        for new_member in message.new_chat_members:
            if not new_member.is_bot():
                context.database.add_member(new_member.id, message.chat.id)


def register_left_member_handler(context: ChatContext):
    @context.bot.message_handler(content_types=['left_chat_member'])
    def handle_new_member(message: telebot.types.Message):
        context.database.remove_member(message.from_user.id, message.chat.id)
