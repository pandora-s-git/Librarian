print("[ LLM ] Loading LLM requirements...")

from huggingface_hub import InferenceClient

class LLM():
    def __init__(self, hf_token: str, prompt_template: str):

        print("[ LLM ] Loading LLM...")

        self.inf = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1", token = hf_token)
        self.prompt_template = prompt_template

        print("[ LLM ] LLM loaded.")

    async def ask(self, txt_docs: str, question, begin: str = ""):

        print("[ LLM ] Asking LLM...")

        ans = ""
        for t in self.inf.text_generation(self.prompt_template.format(txt_docs, question, begin), max_new_tokens=512, stream = True):
            ans+=""
            yield t

        print("[ LLM ] Asked.")

### if you are using 3.11 you might get this error:
###
###     File "C:\Users\USERNAME\AppData\Local\Programs\Python\Python311\Lib\site-packages\huggingface_hub\inference\_common.py", line 272, in _stream_text_generation_response
###         output = TextGenerationStreamResponse(**json_payload)
###                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
###     TypeError: TextGenerationStreamResponse.__init__() got an unexpected keyword argument 'index'
###   
### Temp Fix With:
###     Adding "del json_payload["index"]" just before the error in the _common.py file, it works... it's not an advised fix tho, just something I found after tweaking