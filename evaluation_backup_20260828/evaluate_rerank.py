"""
RAG 评测 v2 — 复刻生产链路（BM25字符级 + bge-m3向量 + RRF → bge-reranker-v2-m3 重排）
用法: cd capstone-ai-kb && source venv/bin/activate && python evaluation/evaluate_rerank.py
"""
import json, os, asyncio, time
import chromadb, requests
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from openai import AsyncOpenAI

load_dotenv()

CHROMA_PATH = "./data/chroma"
COLLECTION_NAME = "kb_1"
TOP_K_VALUES = [3, 5, 10]
RERANK_TOP = 10  # RRF 融合后送重排的候选数（与生产一致）

_client = None
def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            raise SystemExit("ERROR: SILICONFLOW_API_KEY not set")
        _client = AsyncOpenAI(api_key=api_key, base_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"))
    return _client

async def get_embedding(text: str) -> list[float]:
    resp = await get_client().embeddings.create(model="Pro/BAAI/bge-m3", input=text)
    return resp.data[0].embedding

def recall_at_k(retrieved_ids, relevant, k):
    hits = sum(1 for cid in retrieved_ids[:k] if cid in relevant)
    return hits / len(relevant) if relevant else 0.0

async def production_hybrid(collection, query_text):
    """与 app/vector_store.py hybrid_query 一致的数据流（到 RRF top10，不含 rerank）"""
    all_data = collection.get()
    chunk_texts, chunk_ids = all_data["documents"], all_data["ids"]
    # BM25（生产就是字符级 list(doc)）
    bm25 = BM25Okapi([list(d) for d in chunk_texts])
    scores = bm25.get_scores(list(query_text))
    bm25_top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
    bm25_ranks = {chunk_ids[i]: rank for rank, i in enumerate(bm25_top, 1)}
    # 向量路
    emb = await get_embedding(query_text)
    vec_results = collection.query(query_embeddings=[emb], n_results=10)
    vec_ranks = {vec_results["ids"][0][i]: i + 1 for i in range(len(vec_results["ids"][0]))}
    # RRF 融合（与生产 vector_store.py 完全一致的写法：先各自建 top10 dict，缺失项补 0）
    bm25_item = {k: 1/(60+v) for k, v in bm25_ranks.items()}
    vec_item = {k: 1/(60+v) for k, v in vec_ranks.items()}
    total = {k: bm25_item.get(k, 0) + vec_item.get(k, 0)
             for k in set(bm25_item) | set(vec_item)}
    top = sorted(total.items(), key=lambda kv: kv[1], reverse=True)[:RERANK_TOP]
    return [c for c, _ in top]

def rerank(query_text, candidates):
    resp = requests.post(
        "https://api.siliconflow.cn/v1/rerank",
        headers={"Authorization": f"Bearer {os.environ.get('SILICONFLOW_API_KEY')}"},
        json={"model": "BAAI/bge-reranker-v2-m3", "query": query_text, "documents": candidates},
        timeout=30,
    ).json()
    ordered = sorted(resp["results"], key=lambda x: x["relevance_score"], reverse=True)
    return [candidates[r["index"]] for r in ordered]

async def main():
    gt = json.load(open("evaluation/ground_truth.json"))
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Loaded {collection.count()} chunks | Test cases: {len(gt['test_cases'])}")
    old = json.load(open("evaluation/results.json"))  # 旧结果（无 rerank，8/20）

    rows, old_by_id = [], {r["id"]: r for r in old}
    t0 = time.time()
    for i, tc in enumerate(gt["test_cases"], 1):
        qid, question = tc["id"], tc["question"]
        relevant = set(tc["relevant_chunks"])
        hyb_ids = await production_hybrid(collection, question)
        rr_ids = rerank(question, hyb_ids)

        row = {"id": qid, "question": question, "relevant": list(relevant),
               "rrf_retrieved@10": hyb_ids, "reranked": rr_ids}
        for k in TOP_K_VALUES:
            row[f"rrf_R@{k}"] = round(recall_at_k(hyb_ids, relevant, k), 3)
            row[f"rerank_R@{k}"] = round(recall_at_k(rr_ids, relevant, k), 3)
        rows.append(row)
        o = old_by_id[qid]
        d3 = round(row["rerank_R@3"] - o["hybrid_R@3"], 3)
        print(f"Q{qid:2d} R@3: RRF={row['rrf_R@3']:.2f} rerank={row['rerank_R@3']:.2f} (旧hybrid={o['hybrid_R@3']:.2f}, 差{d3:+.2f}) | {question[:24]}")

    print()
    print("=" * 62)
    print("AVERAGE RECALL@K  (50 条)")
    print("=" * 62)
    print(f"{'method':<12}" + "".join(f"R@{k:<7}" for k in TOP_K_VALUES))
    for label, key in [("vector(旧)", "vector"), ("hybrid(旧)", "hybrid"), ("RRF(未重排)", "rrf"), ("rerank(生产链路)", "rerank")]:
        if key in ("vector", "hybrid"):
            vals = [sum(r[f"{key}_R@{k}"] for r in old) / len(old) for k in TOP_K_VALUES]
        else:
            vals = [sum(r[f"{key}_R@{k}"] for r in rows) / len(rows) for k in TOP_K_VALUES]
        print(f"{label:<12}" + "".join(f"{v:.3f}    " for v in vals))

    json.dump(rows, open("evaluation/results_rerank.json", "w"), ensure_ascii=False, indent=2)
    print(f"\n耗时 {time.time()-t0:.0f}s | 已存 evaluation/results_rerank.json")

if __name__ == "__main__":
    asyncio.run(main())
