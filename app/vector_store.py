import chromadb
from openai import AsyncOpenAI
import os

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
