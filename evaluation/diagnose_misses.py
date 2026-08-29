"""诊断 6 条双路皆 miss 的 query：top-5 内容 vs 标注答案，判断标注缺口 or 真难"""
import asyncio
import json
import chromadb
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
data = col.get(include=['documents'])
id_to_doc = dict(zip(data['ids'], data['documents']))
gt = json.load(open('evaluation/ground_truth.json'))
MISS_IDS = [6, 15, 30, 43, 49, 50]


async def main():
    client = AsyncOpenAI(
        api_key=__import__('os').getenv('SILICONFLOW_API_KEY'),
        base_url=__import__('os').getenv('SILICONFLOW_BASE_URL',
                                         'https://api.siliconflow.cn/v1'))
    for tc in gt['test_cases']:
        if tc['id'] not in MISS_IDS:
            continue
        resp = await client.embeddings.create(model='Pro/BAAI/bge-m3',
                                              input=tc['question'])
        r = col.query(query_embeddings=[resp.data[0].embedding], n_results=5)
        print(f"== Q{tc['id']} {tc['question']}")
        print(f"   标注答案: {tc['relevant_chunks']}")
        print(f"   答案原文: {id_to_doc[tc['relevant_chunks'][0]][:70]!r}")
        for cid in r['ids'][0]:
            print(f"   top: {cid}: {id_to_doc[cid][:70]!r}")
        print()


asyncio.run(main())
