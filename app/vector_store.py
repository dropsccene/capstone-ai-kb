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
        # CJK 路由（2026-08-28 评测结论）：字符级 BM25 对"中文 query → 英文语料"
        # 贡献为零（中文单字在英文文本中不可匹配），RRF 中反而挤掉向量路正确答案——
        # 42 条真值评测：纯向量 hit@3/5/10 = 0.76/0.81/0.86 > RRF 0.74/0.76/0.81。
        # 中文走纯向量；英文（同语言词法信号有效）保留 BM25+RRF
        import re
        if re.search(r'[一-鿿]', query_text):
            return await self.query(query_text, top_k)

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
        # rerank（bge-reranker-v2-m3）经两轮 Recall@K 评测确认为负优化
        # （R@3 0.57→0.24 / 0.40→0.28，重排把命中项挤出 top3），已下线，保留 RRF 融合
        top = sorted(total.items(), key=lambda kv: kv[1], reverse=True)
        return [id_to_text[cid] for cid, _ in top[:top_k]]

    
if __name__ == "__main__":
    import asyncio
    q = VectorStore("kb_1")   # 用你类真实名字和参数
    asyncio.run(q.hybrid_query("这篇毕业设计的核心创新点是什么?", top_k=3))




