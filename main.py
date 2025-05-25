# import threading
import multiprocessing
import time

import traceback

import telebot
import random

import datetime

import json
from telebot.types import BotCommand

from hidden import token
from executor import executor

TOKEN = token
bot = telebot.TeleBot(TOKEN)

NN_SWITCH = True

if NN_SWITCH:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, pipeline

    MAX_ATTENTION_MSG_CNT = 50

    chatter_f = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

    # model_name = "deepseek-ai/deepseek-math-7b-instruct"
    model_name = "deepseek-ai/deepseek-llm-7b-chat"
    chatter_t = AutoTokenizer.from_pretrained(model_name)
    chatter = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="cpu")
    chatter.generation_config = GenerationConfig.from_pretrained(model_name)
    chatter.generation_config.pad_token_id = chatter.generation_config.eos_token_id

    model_name = "deepseek-ai/deepseek-math-7b-instruct"
    mather_t = AutoTokenizer.from_pretrained(model_name)
    mather = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="cpu")
    mather.generation_config = GenerationConfig.from_pretrained(model_name)
    mather.generation_config.pad_token_id = mather.generation_config.eos_token_id

# model_name = "deepseek-ai/deepseek-coder-7b-base-v1.5"
# coder_t = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
# coder = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="cpu", trust_remote_code=True)
# coder.generation_config = GenerationConfig.from_pretrained(model_name)
# coder.generation_config.pad_token_id = coder.generation_config.eos_token_id

# model_name = "deepseek-ai/DeepSeek-Prover-V2-7B"
# prover_t = AutoTokenizer.from_pretrained(model_name)
# prover = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="cpu")
# prover.generation_config = GenerationConfig.from_pretrained(model_name)
# prover.generation_config.pad_token_id = prover.generation_config.eos_token_id

recent_messages = dict()

def AddRecentMessageV1(message: telebot.types.Message):
    if (message.text != ""):
        if message.chat.id not in recent_messages:
            recent_messages[message.chat.id] = list()
        while len(recent_messages[message.chat.id]) >= MAX_ATTENTION_MSG_CNT:
            recent_messages[message.chat.id].pop(0)
        recent_messages[message.chat.id].append(
            {"role" : "user",
             "content" : f"<{message.from_user.username}>" + message.text})

def AddRecentMessageV2(chat_id, username, msg_text):
    if (msg_text != ""):
        if chat_id not in recent_messages:
            recent_messages[chat_id] = list()
        while len(recent_messages[chat_id]) >= MAX_ATTENTION_MSG_CNT:
            recent_messages[chat_id].pop(0)
        recent_messages[chat_id].append(
            {"role" : "user",
             "content" : f"<{username}> - " + msg_text})

def AddUser(chat_id, user_id):
    if chat_id not in chat_members:
        chat_members[chat_id] = list()
    if user_id not in chat_members[chat_id]:
        chat_members[chat_id].append(user_id)
        chat_members[chat_id].sort(key=lambda x: bot.get_chat_member(chat_id, x).user.username)
        print(
            f"Added user {user_id} {bot.get_chat_member(chat_id, user_id).user.username} at chat {chat_id}")


def RemoveUser(chat_id, user_id):
    if chat_id not in chat_members:
        return
    if user_id not in chat_members[chat_id]:
        return
    chat_members[chat_id].remove(user_id)
    print(
        f"Removed user {user_id} {bot.get_chat_member(chat_id, user_id).user.username} at chat {chat_id}")

@bot.message_handler(commands=['chat_f'])
def chatter_f_func(message: telebot.types.Message):
    if NN_SWITCH:
        bot.reply_to(message, "NN capabilities are off now")
        return

    print("chatter_f")
    any_message_analyser(message)

    prompt = chatter_f.tokenizer.apply_chat_template([{"role" : "user", "content" : message.text}], tokenize=False, add_generation_prompt=True)
    result = (chatter_f(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95))[0]["generated_text"]
    # print(outputs[0]["generated_text"])

    # result =
    print(result)
    AddRecentMessageV2(message.chat.id, "me(chatter-fast)", result)

    bot.reply_to(message, result)

@bot.message_handler(commands=['chat'])
def chatter_func(message: telebot.types.Message):
    if NN_SWITCH:
        bot.reply_to(message, "NN capabilities are off now")
        return

    print("chatter")
    any_message_analyser(message)
    messages = [
    {"role": "user", "content": "<supervisor> I am your supervisor. Match language your chat is speaking! Just try chatting with everybody! Try to be funny or friendly. Be advised, it is okay to offend somebody. There is a list with messages following. reply ONLY with text of the message you'd like to be delivered to chat members"},
    ]
    if message.chat.id in recent_messages:
        messages = messages + recent_messages[message.chat.id]
    print(*messages, sep = '\n')
    input_tensor = chatter_t.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
    outputs = chatter.generate(input_tensor.to(chatter.device), max_new_tokens=512)

    result = chatter_t.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)

    AddRecentMessageV2(message.chat.id, "me(chatter)", result)

    bot.reply_to(message, result)

@bot.message_handler(commands=['math'])
def chatter_func(message: telebot.types.Message):
    if NN_SWITCH:
        bot.reply_to(message, "NN capabilities are off now")
        return

    print("mather")
    any_message_analyser(message)
    messages = [
    # {"role": "user", "content": "<supervisor> I am your supervisor. You're a math engine of our team."},
    ]
    if message.chat.id in recent_messages:
        messages = messages + recent_messages[message.chat.id]
    print(*messages, sep = '\n')
    input_tensor = mather_t.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
    outputs = mather.generate(input_tensor.to(mather.device), max_new_tokens=512)

    result = mather_t.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)

    AddRecentMessageV2(message.chat.id, "me(mathematician)", result)

    bot.reply_to(message, result)

# @bot.message_handler(commands=['code'])
# def chatter_func(message: telebot.types.Message):
#     print("coder")
#     any_message_analyser(message)
#     messages = [
#     # {"role": "user", "content": "<supervisor> I am your supervisor. You're a math engine of our team."},
#     ]
#     if message.chat.id in recent_messages:
#         messages = messages + recent_messages[message.chat.id]
#     print(*messages, sep = '\n')
#     input_tensor = coder_t.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
#     outputs = coder.generate(input_tensor.to(coder.device), max_new_tokens=512)
#
#     result = coder_t.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
#
#     AddRecentMessageV2(message.chat.id, "deepseek-ai(mathematician)", result)
#
#     bot.reply_to(message, result)
#


@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message: telebot.types.Message):
    for new_member in message.new_chat_members:
        # if not message.from_user.is_bot:
        AddUser(message.chat.id, new_member.id)


# Обработчик для удаления участников
@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(message: telebot.types.Message):
    # if not message.from_user.is_bot:
    RemoveUser(message.chat.id, message.from_user.id)


eng_to_rus = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,.`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>~",
    "йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ"
)
@bot.message_handler(commands=['q'])
def qwerty_cmd(message: telebot.types.Message):

    any_message_analyser(message)

    if message.reply_to_message:
        original_msg = message.reply_to_message
        # bot.reply_to(message, f"Ты ответил на сообщение: '{original_msg.text}'")
        text = original_msg.text
    else:
        bot.reply_to(message, "Это не ответ на сообщение.")

    converted = text.translate(eng_to_rus)
    bot.reply_to(message, converted)


@bot.message_handler(commands=['exec'])
def bot_exec(message: telebot.types.Message):
    any_message_analyser(message)

    bot.reply_to(message, "а не пойти ли тебе нахуй, а? все, лавочка закрыта, пока не зашьют дыры - хуй тебе, понял!?")
    return
    return_manager = multiprocessing.Manager()
    run_result = return_manager.list(["", return_manager.list()])

    code = None
    for i in message.entities:
        if i.type == 'pre' and i.language == 'python':
            code = message.text[i.offset: i.offset + i.length]
            break
    if code == None:
        bot.reply_to(message,
"Запущу твой код на языке python.\n\
Для отправки после комманды напиши Markdown с кодом и меткой языка python.\n\n \
```python\nprint('как-то вот так')```\n\n\
Все print будут заменены на сохранение строки в буффер вывода\n\n\
```\n(print(...) -> __bot_out_buff__.append(...))```\n\n\
Ввод пока невозможен, используй переменные",
        parse_mode="Markdown")
        return
    try:
        task_thread = multiprocessing.Process(target=executor, args=(code,run_result,))
        task_thread.start()
        task_thread.join(5)

        run_result[1] = list(map(str, run_result[1]))
        run_result[1] = '\n'.join(run_result[1])
        if task_thread.is_alive():
            task_thread.terminate()
            bot.reply_to(message,
                            f"Время исполнения истекло. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                            parse_mode="Markdown")
            return
                
        if run_result[0] == "":
            bot.reply_to(message,
                         f"Исполнение программы завершилось успешно. Вот что успела вывести твоя программа:\n\n```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        else:
            bot.reply_to(message,
                         f"Исполнение программы завершилось с ошибкой. Вот сообщение об ошибке:\n\n ```out\n{run_result[0]}``` \n\n Вот что успела вывести твоя программа:\n\n ```out\n{run_result[1]}```",
                         parse_mode="Markdown")
        return
    except Exception as e:
        bot.reply_to(message, f"Блять я маслину поймал:\n\n```{'\n'.join(list(map(str,list(traceback.extract_tb(e.__traceback__))))) + '\n' + '-|-'*10 + '\n' + str(e)}```", parse_mode="Markdown")

@bot.message_handler(commands=['get_member_list'])
def send_member_list(message: telebot.types.Message):
    any_message_analyser(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    if chat_id in chat_members:
        str_of_users_with_indexes = ""
        index = 1
        for cur_user_id in chat_members[chat_id]:
            if is_loud:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    [{bot.get_chat_member(chat_id, cur_user_id).user.username}](tg://user?id={cur_user_id}) \n"
            else:
                str_of_users_with_indexes += "{:>8}".format(
                    index) + f"    {bot.get_chat_member(chat_id, cur_user_id).user.username} \n"
            index += 1
        if is_loud:
            bot.send_message(chat_id, "Вот список всех зарегестрированных участников:\n" + str_of_users_with_indexes,
                             parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "Вот список всех зарегестрированных участников:\n" + str_of_users_with_indexes)
    else:
        bot.send_message(chat_id, "Пока что никого не записал :(")


# Команда /rand выбирает случайного участника
@bot.message_handler(commands=['random'])
def bot_random(message: telebot.types.Message):
    any_message_analyser(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    mentions = [elem for elem in message.entities if elem.type == "mention"]

    if len(mentions) == 0:
        if chat_id in chat_members and chat_members[chat_id]:
            chosen_one = random.choice(list(chat_members[chat_id]))
            if is_loud:
                bot.send_message(chat_id,
                                 f"🎲 Случайный выбор: [{bot.get_chat_member(chat_id, chosen_one).user.username}](tg://user?id={chosen_one})",
                                 parse_mode="Markdown")
            else:
                bot.send_message(chat_id,
                                 f"🎲 Случайный выбор: {bot.get_chat_member(chat_id, chosen_one).user.username}")
        else:
            bot.send_message(chat_id, "Не могу выбрать никого, недостаточно данных 🫤")
    else:
        chosen_mention = random.choice(mentions)
        # chosen_mention = telebot.types.MessageEntity()
        response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

        bot.send_message(chat_id, f"Случайный выбор: {response_msg}")


@bot.message_handler(commands=['uptime'])
def bot_uptime(message: telebot.types.Message):
    any_message_analyser(message)
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Я запущен уже {datetime.timedelta(seconds= time.time() - start_time)}")

@bot.message_handler(commands=['shuffle'])
def bot_shuffle(message: telebot.types.Message):
    any_message_analyser(message)
    chat_id = message.chat.id

    is_loud = "-loud" in message.text

    mentions = [elem for elem in message.entities if elem.type == "mention"]

    if len(mentions) == 0:
        if chat_id in chat_members and chat_members[chat_id]:
            chosen_order = chat_members[chat_id]
            for i in range(int(len(chosen_order) ** 0.5 + 1)):
                random.shuffle(chosen_order)
            message = "Случайный порядок:\n"
            index = 1
            for i in chosen_order:
                if is_loud:
                    message += "{:>8}".format(
                        index) + f"    [{bot.get_chat_member(chat_id, i).user.username}](tg://user?id={i}) \n"
                else:
                    message += "{:>8}".format(
                        index) + f"    {bot.get_chat_member(chat_id, i).user.username} \n"
                index += 1
            if is_loud:
                bot.send_message(chat_id,
                                 message,
                                 parse_mode="Markdown")
            else:
                bot.send_message(chat_id,
                                 message)
        else:
            bot.send_message(chat_id, "Не могу выбрать никого, недостаточно данных 🫤")
    else:
        chosen_mention = random.choice(mentions)
        # chosen_mention = telebot.types.MessageEntity()
        response_msg = message.text[chosen_mention.offset:chosen_mention.offset + chosen_mention.length]

        bot.send_message(chat_id, f"Случайный порядок: {response_msg}")


# Запоминаем участников, когда они что-то пишут
@bot.message_handler()
def any_message_analyser(message: telebot.types.Message):
    # print(message)
    if NN_SWITCH:
        AddRecentMessageV1(message)

    chat_id = message.chat.id
    user_id = message.from_user.id
    if not message.from_user.is_bot:
        AddUser(chat_id, user_id)


if __name__ == "__main__":
    commands = [
        BotCommand("random", "Get random member from all registered, or choose one from mentioned after command"),
        BotCommand("shuffle",
                   "Get random order from all registered members, or random order of mentioned after command"),
        BotCommand("get_member_list", "Get list of all registered members"),
        BotCommand("exec", "Run your python code!"),
        BotCommand("q", "qwerty -> йцукен"),
        BotCommand("uptime", "For how long I have been standing?"),
    ]
    try:
        bot.set_my_commands(commands)
    except Exception as e:
        print(f"failed to set commands annotation: \n\n {e}")
    try:
        chat_members_df = open("chat_members.json", mode='r')
        chat_members = json.load(chat_members_df)
        chat_members_df.close()

        # chat_members = dict()
        for key in list(chat_members.keys()):
            chat_members[int(key)] = sorted(chat_members[key], key=lambda x: bot.get_chat_member(key, x).user.username)
            chat_members.pop(key)

        print("data loaded successfully")
    except Exception as e:
        chat_members = dict()
        print(f"failed to read data: \n\n {e}")

    # bot.infinity_polling()
    try:
        start_time = time.time()
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("manually stopped")
    except Exception as e:
        print(f"got unexpected error: \n\n {e} \n \n {str(e)}")

    try:
        chat_members_df = open("chat_members.json", mode='w')
        chat_members_df.truncate()
        json.dump(chat_members, chat_members_df, indent=4)
        chat_members_df.close()
        print("successfully dumped data")
    except Exception as e:
        print(f"data dump failed: \n\n {e}")
