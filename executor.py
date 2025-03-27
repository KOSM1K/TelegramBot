import traceback

def executor(code: str, run_result: list):
        banned_samples = sorted([
            "import",
            "open",
            "exec",
            "eval",
            "builtins",
            "os",
            "sys",
            "getattr",
            "system",
            "globals",
            "telebot"
        ])

        refined_code = code.replace("print", "run_result[1].append")
        # refined_code = code
        print(refined_code)
        if any(i in refined_code for i in banned_samples):
            run_result[0] = "бан тебе нахуй педрила, нельзя такой код писать"
            run_result[1] = list()
            return
        try:
            context = {"run_result": run_result,
                       "banned_samples" : list(banned_samples[:])
                       }
            exec(compile(refined_code, "<user_input>", "exec", dont_inherit = True, optimize = 2), context)
            # __bot_out_buff__ = context["__bot_out_buff__"]
            run_result[0] = ""
            # run_result[1] 
            return
        except Exception as e:
            # __bot_out_buff__ = context["__bot_out_buff__"]
            run_result[0] = '\n'.join(list(map(str,list(traceback.extract_tb(e.__traceback__))))) + '\n' + '-|-'*10 + '\n' + str(e)
            # run_result[1] = __bot_out_buff__
            return
        # return run_result
