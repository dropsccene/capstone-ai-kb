"""跨语言诊断：中 query vs 英 query 的向量检索 top3 对比（5 条代表）"""
import asyncio
import chromadb
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')

PAIRS = [
    ('什么是装饰器？', 'What is a decorator?'),
    ('如何使用 venv 创建虚拟环境？', 'How to create a virtual environment with venv?'),
    ('如何读写文本文件？', 'How to read and write text files?'),
    ('json 模块怎么用？', 'How to use the json module?'),
    ('os 模块有哪些常用功能？', 'What are common functions of the os module?'),
]


async def t():
    client = AsyncOpenAI(
        api_key=__import__('os').getenv('SILICONFLOW_API_KEY'),
        base_url=__import__('os').getenv('SILICONFLOW_BASE_URL',
                                         'https://api.siliconflow.cn/v1'))
    for zh, en in PAIRS:
        for label, q in [('zh', zh), ('en', en)]:
            resp = await client.embeddings.create(model='Pro/BAAI/bge-m3', input=q)
            emb = resp.data[0].embedding
            r = col.query(query_embeddings=[emb], n_results=3)
            cids = r['ids'][0]
            print(f"{label} | {q[:16]:<18} -> top3: {cids}")
        print()


asyncio.run(t())
