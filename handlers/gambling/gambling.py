from handlers.gambling.balance import *
from handlers.gambling.send import *
from handlers.gambling.leaderboard import *
from handlers.gambling.slots import *
from handlers.gambling.daily import *


def register_gambling_commands(context: ChatContext):
    register_gambling_send_command(context)
    register_gambling_balance_command(context)
    register_gambling_leaderboard_command(context)
    register_gambling_slots_command(context)
    register_gambling_daily_action(context)
