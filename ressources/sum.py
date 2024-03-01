print("[ SUM ] Loading SUM Requirements...")

## from transformers import RobertaTokenizerFast, EncoderDecoderModel  # in case u wanna use a french one
from transformers import pipeline

class SUM():
    def __init__(self):

        print("[ SUM ] Loading model for summarization...")

        ## ckpt = 'mrm8488/camembert2camembert_shared-finetuned-french-summarization'
        ## tokenizer = RobertaTokenizerFast.from_pretrained(ckpt)
        ## self.tokenizer = tokenizer
        ## self.model = EncoderDecoderModel.from_pretrained(ckpt).to("cpu")

        ckpt = "facebook/bart-large-cnn"
        self.model = pipeline("summarization", model = ckpt)

    def _generate_summary(self, text):
        ## inputs = self.tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
        ## input_ids = inputs.input_ids.to("cpu")
        ## attention_mask = inputs.attention_mask.to("cpu")
        ## output = self.model.generate(input_ids, attention_mask=attention_mask)
        ## return self.tokenizer.decode(output[0], skip_special_tokens=True)

        return "".join(list(self.model(text, max_length=256, min_length=32, do_sample=False)[0]["summary_text"]))

    def sum(self, txt: str):

        print("[ SUM ] Summarizing contents...")

        res = self._generate_summary(txt)

        return res