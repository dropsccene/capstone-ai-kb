import chromadb
from openai import AsyncOpenAI
import os
from rank_bm25 import BM25Okapi



# 硅基流动 Embedding API（异步）
_embedding_client = None


def _get_embedding_client():
    global _embedding_client
    if _embedding_client is None:
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        if not api_key:
            raise RuntimeError("SILICONFLOW_API_KEY 环境变量未设置")
        _embedding_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return _embedding_client


async def get_embedding(text: str) -> list[float]:
    """调用硅基流动 BGE-M3 模型，返回 embedding 向量"""
    client = _get_embedding_client()
    response = await client.embeddings.create(
        model="Pro/BAAI/bge-m3",
        input=text,
    )
    return response.data[0].embedding


class VectorStore():
    def __init__(self, collection_name="default", path="./data/chroma"):
        self.client = chromadb.PersistentClient(path)
        self.collection = self.client.get_or_create_collection(collection_name)

    async def add_chunks(self, chunks: list[str], doc_id: int):
        for i, chunk in enumerate(chunks):
            embedding = await get_embedding(chunk)
            self.collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"doc_id": doc_id, "chunk_index": i}],
                ids=[f"chunk_{doc_id}_{i}"]
            )

    async def query(self, query_text: str, top_k: int = 3):
        embedding = await get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results["documents"][0]

    async def hybrid_query(self,query_text:str,top_k:int=3):
        # 1. 获取所有 chunk 原文
        chunks = self.collection.get()
        chunk_texts = chunks["documents"]
        chunk_ids = chunks["ids"]
        chunk_metadatas = chunks["metadatas"]
        id_to_text = dict(zip(chunk_ids, chunk_texts))

        # 2. BM25 检索
        bm25tokenized = [list(doc) for doc in chunk_texts]
        bm25 = BM25Okapi(bm25tokenized)
        bm25_scores = bm25.get_scores(list(query_text))
        bm25_top_k = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
        bm25_enumerate = list(enumerate(bm25_top_k, 1))
        bm25_ranks = {chunk_ids[i]:m for m, i in bm25_enumerate}
        # 3. 向量路
        embedding = await get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=10
        )
        vector_ranks = {results["ids"][0][i]:i+1 for i in range(len(results["ids"][0]))}
        # 4. RRF 融合
        # 每路把"名次"翻成"RRF 项" 1/(60+名次)
        bm25_item = {k: 1/(60+v) for k,v in bm25_ranks.items()}
        vector_item = {k: 1/(60+v) for k,v in vector_ranks.items()}
        # 并集里每个 id，两路的项相加（缺哪路 .get 补 0）
        total = {k:bm25_item.get(k,0)+vector_item.get(k,0) for k in set(bm25_item)|set(vector_item)}
        # 按总分排序，取前 top_k
        top = sorted(total.items(),key=lambda kv:kv[1],reverse=True)[:top_k]
        # 返回 top_k 的原文
        return [id_to_text[k] for k,v in top]
        

        
