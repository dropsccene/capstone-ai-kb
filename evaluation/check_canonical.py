"""找 Q15/Q43/Q50 的权威答案章节，验证内容后决定是否补标注，并查其排名"""
import asyncio
import json
import chromadb
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
data = col.get(include=['documents'])
ids, docs = data['ids'], data['documents']

# 按内容特征找权威章节（不是按检索排名找）
PROBES = {
    43: ['closure'],           # glossary closure 条目
    50: ['Keywords and soft'],  # reference 关键字章节标题
    15: ['union, intersection'],  # 集合运算正文
}

for qid, needles in PROBES.items():
    print(f"== Q{qid} 权威章节定位:")
    for i, d in enumerate(docs):
        low = d.lower()
        if all(n.lower() in low for n in needles):
            print(f"   {ids[i]}: {d[:100]!r}")
    print()


async def rank_of():
    """查这些权威 chunk 在对应 query 的 top-10 排名"""
    client = AsyncOpenAI(
        api_key=__import__('os').getenv('SILICONFLOW_API_KEY'),
        base_url=__import__('os').getenv('SILICONFLOW_BASE_URL',
                                         'https://api.siliconflow.cn/v1'))
    gt = {t['id']: t for t in json.load(open('evaluation/ground_truth.json'))['test_cases']}
    for qid in (43, 50, 15):
        q = gt[qid]['question']
        resp = await client.embeddings.create(model='Pro/BAAI/bge-m3', input=q)
        r = col.query(query_embeddings=[resp.data[0].embedding], n_results=10)
        print(f"Q{qid} top-10: {r['ids'][0]}")


asyncio.run(rank_of())
