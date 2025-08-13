import os

from chat_context import *
from handlers import *

BOT_TOKEN = os.getenv("BOT_TOKEN")

if (BOT_TOKEN == None):
    try:
        from hidden import token
        BOT_TOKEN = token
    except:
        raise "Couldn't find bot token. I give up."

chat_context = ChatContext(BOT_TOKEN)

if __name__ == "__main__":
    register_rage_command(chat_context)
    register_qwerty_command(chat_context)
    register_random_member_command(chat_context)
    register_shuffle_members_command(chat_context)
    register_list_members_command(chat_context)
    register_uptime_command(chat_context)
    register_exec_command(chat_context)
    register_probability_command(chat_context)
    register_choose_from_command(chat_context)
    register_gambling_commands(chat_context)

    chat_context.launch()
