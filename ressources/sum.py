print("[ SUM ] Loading SUM Requirements...")

from transformers import RobertaTokenizerFast, EncoderDecoderModel

class SUM():
    def __init__(self):

        print("[ SUM ] Loading model for summarization...")

        ## ckpt = 'mrm8488/camembert2camembert_shared-finetuned-french-summarization' in case u wanna use a french one
        ckpt = "facebook/bart-large-cnn"
        tokenizer = RobertaTokenizerFast.from_pretrained(ckpt)
        model = EncoderDecoderModel.from_pretrained(ckpt).to("cpu")
        self.tokenizer = tokenizer
        self.model = model 

    def _generate_summary(self, text):
        inputs = self.tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
        input_ids = inputs.input_ids.to("cpu")
        attention_mask = inputs.attention_mask.to("cpu")
        output = self.model.generate(input_ids, attention_mask=attention_mask)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def sum(self, txt: str):

        print("[ SUM ] Summarizing contents...")

        res = self._generate_summary(txt)

        return res