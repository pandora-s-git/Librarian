print("[ SUM ] Loading SUM Requirements...")

from transformers import RobertaTokenizerFast, EncoderDecoderModel
from transformers import pipeline

class SUM():
    def __init__(self, lang: str = "en"):
        assert lang in ["en","fr"]

        print("[ SUM ] Loading model for summarization...")

        self.lang = lang

        if lang == "en":
            ckpt = "facebook/bart-large-cnn"
            self.model = pipeline("summarization", model = ckpt)
        else:
            ckpt = 'mrm8488/camembert2camembert_shared-finetuned-french-summarization'
            tokenizer = RobertaTokenizerFast.from_pretrained(ckpt)
            self.tokenizer = tokenizer
            self.model = EncoderDecoderModel.from_pretrained(ckpt).to("cpu")

    def _generate_sum_params(self, text, max_tokens: int, min_tokens: int):
        if self.lang == "en":
            assert max_tokens > min_tokens
            return "".join(list(self.model(text, max_length=max_tokens, min_length=min_tokens, do_sample=False)[0]["summary_text"]))
        else:
            inputs = self.tokenizer([text], padding="max_length", truncation=True, max_length=max_tokens, return_tensors="pt")
            input_ids = inputs.input_ids.to("cpu")
            attention_mask = inputs.attention_mask.to("cpu")
            output = self.model.generate(input_ids, attention_mask=attention_mask)
            return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def sum(self, txt: str):

        print("[ SUM ] Summarizing main contents...")

        res = self._generate_sum_params(txt, 256, 64)

        return res