print("[ RAG ] Loading RAG requirements...")

import os
from tqdm import tqdm
from ressources.vdb import VDB
from ressources.sum import SUM
from ressources.llm import LLM

class RAG():
    def __init__(self, library: str, context_c_size: int = 10000, lang: str = "en"):
        assert lang in ["en","fr"]

        print("[ RAG ] Loading RAG...")

        self.vdb = VDB()
        self.sum = SUM()
        if lang == "en":
            self.llm = LLM("<s>[INST] Here is a list of documents to use to answer a question:\n{}\nUsing these documents, answer the following question clearly and briefly, a summary. Question you need to answer:\n{} [/INST] {}")
            self.pre = "Here is the answer:\n"
        else:
            self.llm = LLM("<s>[INST] Voici une liste de documents à utiliser pour répondre à une question :\n{}\nEn utilisant ces documents, répondez clairement et brièvement à la question suivante, en résumant. Question à laquelle vous devez répondre :\n{} [/INST] {}")
            self.pre = "Voici la réponse:\n"
        self.context = context_c_size
        self.library = library

        print("[ RAG ] RAG Loaded.")

    def cut_document(self, input_string):
        max_length = self.context//2
        result = []
        while input_string:
            result.append(input_string[:max_length])
            input_string = input_string[max_length:]
        final = []
        for i in range(len(result)-1):
            temp = result[i]+result[i+1]
            final.append(temp)
        if len(result) == 1:
            final = result
        return final
    
    async def load(self, library: str = None):
        if library == None:
            library = self.library
        async for feed in self.vdb.update_vector_database(library):
            yield feed

    async def ask(self, question: str, n_docs_max: int = 1, threshold_full: int = 85, threshold_sum: int = 70):
        assert threshold_full >= threshold_sum

        print("[ RAG ] Querying VDB...")

        async for feed in self.vdb.query(question, self.library, n_docs_max):
            yield feed
        docs = feed

        print("[ RAG ] Filtering documents...")

        docs_full_sum = []
        for d in docs:
            if d["score"] >= threshold_sum:
                docs_full_sum.append(d)

        print("[ RAG ] Cutting into smaller sections...")

        if not os.path.exists(self.library+"/cuts"):
            os.makedirs(self.library+"/cuts")

        for d in tqdm(docs_full_sum):
            cuts = self.cut_document(d["content"])
            for j in range(len(cuts)):
                try:
                    with open(self.library+"/cuts/"+f"{d['document']}(){j}.txt", "r", encoding="utf-8") as f:
                        previous = f.read()
                except FileNotFoundError:
                    previous = ""

                if cuts[j] != previous:
                    with open(self.library+"/cuts/"+f"{d['document']}(){j}.txt", "w", encoding="utf-8") as f:
                        f.write(cuts[j])
                else:

                    print("[ RAG ] Section already exists & to date.")

        print("[ RAG ] Querying sections VDB...")

        async for feed in self.vdb.query(question, self.library+"/cuts", n_docs_max, [d["document"] for d in docs_full_sum]):
            yield feed
        sections_full_sum = feed

        print("[ RAG ] Filtering sections of documents...")

        contents_full = []
        contents_sum = []
        for d in sections_full_sum:
            if  threshold_full > d["score"] >= threshold_sum:
                contents_sum.append(d)
            elif d["score"] >= threshold_full:
                contents_full.append(d)
        
        print("[ RAG ] Summarizing contents...")

        contents_summed = []
        for d in tqdm(contents_sum):
            content = [d["content"]]
            while True:
                try:
                    summs = ""
                    for c in content:
                        s = self.sum.sum(c)
                        summs += s
                        yield
                    break
                except IndexError:
                    new_content = []
                    for c in content:
                        new_content.append(c[:len(c)//2])
                        new_content.append(c[len(c)//2:])
                    content = new_content
            d["content"] = summs
            contents_summed.append(d)
            yield d["document"]

        yield "<|asking|>"

        print("[ RAG ] Asking LLM...")

        all_contents = contents_full+contents_summed
        prompt = "\n".join([d["document"].split("()")[0]+"\n"+d["content"] for d in all_contents[::-1]])

        async for feed in self.llm.ask(prompt, question, self.pre):
            yield feed

        yield [d["document"] for d in all_contents]

        print("[ RAG ] Finished.")
        



        

