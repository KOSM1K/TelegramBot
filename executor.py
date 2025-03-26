def executor(code: str, run_result: list):
        __bot_out_buff__ = []
        banned_samples = {
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
        }

        refined_code = code.replace("print", "__bot_out_buff__.append")
        # refined_code = code
        print(refined_code)
        if any(i in refined_code for i in banned_samples):
            run_result[0] = "бан тебе нахуй педрила, нельзя такой код писать"
            run_result[1] = __bot_out_buff__
            return
        try:
            exec(refined_code)
            run_result[0] = ""
            run_result[1] = __bot_out_buff__
        except Exception as e:
            run_result[0] = str(e)
            run_result[1] = __bot_out_buff__
        # return run_result
