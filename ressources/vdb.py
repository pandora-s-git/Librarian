print("[ VDB ] Loading VDB requirements...")

import ast
import datetime
import numpy as np
import faiss
import os
from tqdm import tqdm 
from sentence_transformers import SentenceTransformer

class VDB():
    def __init__(self, char_doc_size: int = 10000):

        print("[ VDC ] Loading VDB...")

        self.context = char_doc_size

        print("[ VDB ] Loading model for embedding...")

        self.model = SentenceTransformer('intfloat/multilingual-e5-large-instruct')

        print("[ VDB ] VDB loaded.")

    def generate_embedding(self, txt: str) -> list[float]:
        emb = self.model.encode(txt, convert_to_tensor=False, normalize_embeddings=True, convert_to_numpy=True)
        return list(emb)

    async def update_vector_database(self, library: str, specify: list = None):
        vector_database = self._get_vector_database(library, None)
        updated_vector_database = []
        for file in tqdm([file for file in os.listdir(library) if file.endswith(".txt")]):
            cached = False
            for d in vector_database:
                if d["document"] == file:
                    cached = True

                    print("[ VDB ] Document Cached.")

                    if (not(specify == None or file.replace(".txt","").split("-")[0] in specify)):

                        print("[ VDB ] Document not required. Skip.")

                        updated_vector_database.append({"document":file, "date": d["date"],"vector":d["vector"]})
                    else:

                        date = datetime.datetime.fromtimestamp(os.stat(library+"/"+file).st_mtime)

                        if str(d["date"]) != str(date):

                            print("[ VDB ] Document modified. Updating vectors...")

                            with open(library+"/"+file, "r", encoding="utf-8") as f:
                                updated_vector_database.append({"document":file, "date": date,"vector":self.generate_embedding(f.read())})
                        else:

                            print("[ VDB ] Document to date.")

                            updated_vector_database.append({"document":d["document"], "date": d["date"],"vector":d["vector"]})
                        yield file
                        break
            if not cached:
                 
                print("[ VDB ] Document not cached. Updating vectors...")

                date = datetime.datetime.fromtimestamp(os.stat(library+"/"+file).st_mtime)

                with open(library+"/"+file, "r", encoding="utf-8") as f:
                    updated_vector_database.append({"document":file, "date": date,"vector":self.generate_embedding(f.read())})
                yield file
                    
        with open(library+"/vector_database", "w", encoding="utf-8") as f:
            f.write("\n".join([f"{v['document']}|{v['date']}|{v['vector']}" for v in updated_vector_database]))
        yield vector_database
    
    def _get_vector_database(self, library: str, specify: list):
        try:
            with open(library+"/vector_database", "r", encoding="utf-8") as f:
                vector_database = [{"document":v.strip().split("|")[0], "date": v.strip().split("|")[1],"vector":ast.literal_eval(v.strip().split("|")[2])} for v in f.readlines() if specify == None or v.strip().split("|")[0].split("()")[0] in specify]
        except FileNotFoundError:

            print("[ VDB ] No database cached. Creating new one.")

            vector_database = []

        return vector_database
    
    def _get_vectors(self, vector_database: list):
        return np.array([v["vector"] for v in vector_database]).astype('float32')
    
    def _get_query_vector(self, query: str):
        v = self.generate_embedding(query)
        return np.array([v]).astype('float32')
  
    def _get_distances(self, vectors: np.ndarray, query_vector: np.ndarray, n: int):
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        distances, indices = index.search(query_vector, n)
        return distances, indices
  
    def _normalize_distances_to_scores(self, distances, min_score=0, max_score=100):
        if len(distances) == 1:
            return [max_score]
        min_distance = min(distances)
        max_distance = max(distances)
        normalized_scores = [
            min_score + (max_score - min_score) * (max_distance - distance) / (max_distance - min_distance)
            for distance in distances
        ]
        return normalized_scores
    
    def query_documents(self, q_text: str, library: str, n: int, specify: list = None):
        vectors_database = self._get_vector_database(library, specify)
        vectors = self._get_vectors(vectors_database)
        query_vector = self._get_query_vector(q_text)
        distances, indices = self._get_distances(vectors, query_vector, n*20)
        indices = [i for i in indices[0] if int(i) >= 0]
        distances = distances[0][:len(indices)]
        scores = self._normalize_distances_to_scores(distances)
        print(scores)
        if len(indices) == 1:
            return [(vectors_database[int(indices[0])]["document"],vectors_database[int(indices[0])]["date"],scores[0])]
        results = [(vectors_database[int(i)]["document"],vectors_database[int(i)]["date"],scores[j]) for j, i in enumerate(indices)]
        return results[:n]
  
    async def query(self, q_text: str, library: str, n_docs_max: int = 1, specify: list = None):

        print("[ VDB ] Updating vector database...")

        async for feed in self.update_vector_database(library, specify):
            yield feed
        documents = self.query_documents(q_text, library, n_docs_max, specify)
        contents = []

        print("[ VDB ] Getting documents content...")

        for d, date, s in tqdm(documents):
            with open(library+"/"+d, "r", encoding="utf-8") as f:
                contents.append({"document":d.strip(".txt"),"date": date,"content":f.read(), "score": s})

        print("[ VDB ] Query Completed.")

        yield contents