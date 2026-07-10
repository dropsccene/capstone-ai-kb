import chromadb
import os
from sentence_transformers import SentenceTransformer
import asyncio


_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2",local_files_only=True)
    return _model

def get_embedding(text:str):
    return _get_model().encode(text).tolist()

class VectorStore():
    def __init__(self,collection_name="default",path="./data/chroma"):
        self.client = chromadb.PersistentClient(path)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_chunks(self,chunks:list[str],doc_id:int):
        for i,chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            self.collection.add(
                documents = [chunk],
                embeddings = [embedding],
                metadatas = [{"doc_id": doc_id, "chunk_index": i}],
                ids = [f"chunk_{doc_id}_{i}"]
            )
    
    def query(self,query_text:str,top_k:int = 3):
        embedding = get_embedding(query_text)
        results = self.collection.query(
            query_embeddings = [embedding],
            n_results = top_k
        )
        return results["documents"][0]
