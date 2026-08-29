"""实验：纯向量 vs RRF（当前 BM25 路对中文 query 可能是死重）
在当前语料 + 42 条 GT 上跑，输出 hit@K 对比 + 双路都 miss 的案例清单
"""
import asyncio
import json
import chromadb
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
gt = json.load(open('evaluation/ground_truth.json'))


async def main():
    client = AsyncOpenAI(
        api_key=__import__('os').getenv('SILICONFLOW_API_KEY'),
        base_url=__import__('os').getenv('SILICONFLOW_BASE_URL',
                                         'https://api.siliconflow.cn/v1'))
    vec_hits = {3: 0, 5: 0, 10: 0}
    misses = []
    for tc in gt['test_cases']:
        q = tc['question']
        relevant = set(tc['relevant_chunks'])
        resp = await client.embeddings.create(model='Pro/BAAI/bge-m3', input=q)
        r = col.query(query_embeddings=[resp.data[0].embedding], n_results=10)
        top = r['ids'][0]
        for k in (3, 5, 10):
            if set(top[:k]) & relevant:
                vec_hits[k] += 1
        if not set(top) & relevant:
            misses.append((tc['id'], q, list(relevant)))

    n = len(gt['test_cases'])
    print(f"纯向量 hit@K（{n} 条）:")
    for k in (3, 5, 10):
        print(f"  hit@{k}: {vec_hits[k]/n:.3f}")
    print(f"\n纯向量也 miss 的 {len(misses)} 条:")
    for qid, q, rel in misses:
        print(f"  Q{qid}: {q}  答案: {rel}")


asyncio.run(main())
