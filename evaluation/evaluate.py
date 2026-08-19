"""
RAG 评估脚本 — Recall@K
用法: cd capstone-ai-kb && source venv/bin/activate && python evaluation/evaluate.py
"""
import json
import asyncio
import chromadb
from openai import AsyncOpenAI
import os
import sys

# --- Config ---
CHROMA_PATH = "./data/chroma"
COLLECTION_NAME = "kb_1"
TOP_K_VALUES = [3, 5, 10]

# --- Embedding (复用项目的硅基流动 BGE-M3) ---
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        if not api_key:
            print("ERROR: SILICONFLOW_API_KEY not set")
            sys.exit(1)
        _client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return _client

async def get_embedding(text: str) -> list[float]:
    client = get_client()
    response = await client.embeddings.create(
        model="Pro/BAAI/bge-m3",
        input=text,
    )
    return response.data[0].embedding

# --- Recall@K ---
def recall_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    """前 K 条中命中相关 chunk 的比例"""
    hits = sum(1 for cid in retrieved_ids[:k] if cid in relevant)
    return hits / len(relevant) if relevant else 0.0

# --- 向量检索 ---
async def vector_retrieve(collection, query_text: str, top_k: int) -> list[str]:
    embedding = await get_embedding(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results["ids"][0]

# --- 混合检索 (BM25 + RRF) ---
async def hybrid_retrieve(collection, query_text: str, top_k: int) -> list[str]:
    from rank_bm25 import BM25Okapi

    all_data = collection.get()
    chunk_texts = all_data["documents"]
    chunk_ids = all_data["ids"]

    # BM25
    tokenized = [list(doc) for doc in chunk_texts]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(list(query_text))
    bm25_top = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
    bm25_ranks = {chunk_ids[i]: rank for rank, i in enumerate(bm25_top, 1)}

    # 向量
    embedding = await get_embedding(query_text)
    vec_results = collection.query(query_embeddings=[embedding], n_results=10)
    vec_ranks = {vec_results["ids"][0][i]: i + 1 for i in range(len(vec_results["ids"][0]))}

    # RRF 融合
    bm25_rrf = {k: 1 / (60 + v) for k, v in bm25_ranks.items()}
    vec_rrf = {k: 1 / (60 + v) for k, v in vec_ranks.items()}
    total = {k: bm25_rrf.get(k, 0) + vec_rrf.get(k, 0)
             for k in set(bm25_rrf) | set(vec_rrf)}
    top = sorted(total.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [k for k, v in top]

# --- Main ---
async def run_evaluation():
    # Load ground truth
    with open("evaluation/ground_truth.json", "r") as f:
        gt = json.load(f)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Loaded {collection.count()} chunks from {COLLECTION_NAME}")
    print(f"Test cases: {len(gt['test_cases'])}")
    print()

    results = []

    for tc in gt["test_cases"]:
        qid = tc["id"]
        question = tc["question"]
        relevant = set(tc["relevant_chunks"])

        # 两种检索方式
        vec_ids = await vector_retrieve(collection, question, max(TOP_K_VALUES))
        hyb_ids = await hybrid_retrieve(collection, question, max(TOP_K_VALUES))

        row = {"id": qid, "question": question, "relevant": list(relevant)}

        for method_name, retrieved in [("vector", vec_ids), ("hybrid", hyb_ids)]:
            for k in TOP_K_VALUES:
                r = recall_at_k(retrieved, relevant, k)
                row[f"{method_name}_R@{k}"] = round(r, 3)
                row[f"{method_name}_retrieved@{k}"] = retrieved[:k]

        results.append(row)

        # 打印单条结果
        print(f"Q{qid}: {question}")
        print(f"  Relevant: {relevant}")
        for method in ["vector", "hybrid"]:
            r3 = row[f"{method}_R@3"]
            r5 = row[f"{method}_R@5"]
            r10 = row[f"{method}_R@10"]
            print(f"  {method:7s} R@3={r3:.3f}  R@5={r5:.3f}  R@10={r10:.3f}")
        print()

    # 汇总
    print("=" * 60)
    print("AVERAGE RECALL@K")
    print("=" * 60)
    for method in ["vector", "hybrid"]:
        for k in TOP_K_VALUES:
            avg = sum(r[f"{method}_R@{k}"] for r in results) / len(results)
            print(f"  {method:7s} R@{k:2d} = {avg:.3f}")
    print()

    # 保存详细结果
    with open("evaluation/results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Detailed results saved to evaluation/results.json")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
