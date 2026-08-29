"""
Ground Truth 建议标注生成器（B 方案）
====================================
对 50 条候选 query，用两条独立于评测检索器的信号生成「建议相关 chunk」：
  信号A 关键词包含：query 中的英文专有名词/关键词在 chunk 原文中出现
  信号B 向量相似度：bge-m3 余弦 top-10
两条信号交叉取 top 候选，输出供人工复核（人工复核后才写入 ground_truth.json）。
用法: cd capstone-ai-kb && source venv/bin/activate && python evaluation/generate_gt_suggestions.py
"""
import asyncio, json, re
import chromadb
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

CHROMA_PATH = "./data/chroma"

STOP_WORDS = {
    "how", "what", "the", "is", "are", "to", "of", "and", "in", "a", "an",
    "which", "do", "does", "can", "with", "for", "on", "at", "that", "this",
    "it", "or", "not", "be", "you", "your", "python", "使用", "如何", "怎么",
    "什么", "哪些", "为什么", "区别", "含义", "写法", "有没有", "多少", "是",
}


def get_chroma():
    c = chromadb.PersistentClient(path=CHROMA_PATH)
    return c.get_collection("kb_1")


def extract_keywords(query: str) -> list[str]:
    """从 query 提取英文关键词（含下划线 token 如 sys.argv / *args）"""
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_.]{1,20}", query)
    return [t for t in tokens if t.lower() not in STOP_WORDS]


async def get_embedding(text: str) -> list[float]:
    client = AsyncOpenAI(
        api_key=__import__("os").getenv("SILICONFLOW_API_KEY"),
        base_url=__import__("os").getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
    )
    resp = await client.embeddings.create(model="Pro/BAAI/bge-m3", input=text)
    return resp.data[0].embedding


def parse_candidates():
    raw = open("evaluation/gt_candidates.md", encoding="utf-8").read()
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", raw, re.M)
    return [(int(n), q.strip()) for n, q, _ in rows if n.isdigit()]


async def main():
    col = get_chroma()
    all_data = col.get(include=["documents"])
    ids, docs = all_data["ids"], all_data["documents"]
    id_to_doc = dict(zip(ids, docs))
    print(f"语料 {len(ids)} chunks | 候选 query 解析中...")

    qs = parse_candidates()
    print(f"解析到 {len(qs)} 条 query")

    suggestions = []
    for qid, query in qs:
        kws = extract_keywords(query)
        # 信号A：关键词包含匹配（全部关键词都出现 > 部分出现）
        def kw_score(doc: str) -> int:
            low = doc.lower()
            return sum(1 for k in kws if k.lower() in low)

        # 取关键词命中前 5
        kw_hits = sorted(((kw_score(d), i) for i, d in enumerate(docs)),
                         reverse=True)[:5]
        kw_top = [(ids[i], s) for s, i in kw_hits if s > 0]

        # 信号B：向量 top-10
        emb = await get_embedding(query)
        vec = col.query(query_embeddings=[emb], n_results=10)
        vec_top = list(zip(vec["ids"][0], vec["distances"][0]))

        # 合并：向量 top 中关键词也命中的优先，其余按向量距离
        vec_ids = [v[0] for v in vec_top]
        merged = [vid for vid, _ in kw_top if vid in vec_ids] + \
                 [vid for vid, _ in vec_top if vid not in [v[0] for v in kw_top]]
        # 去重保序，取前 3 作为建议
        seen, sugg = set(), []
        for vid in merged:
            if vid not in seen:
                seen.add(vid); sugg.append(vid)
            if len(sugg) >= 3:
                break
        suggestions.append({
            "id": qid, "question": query, "keywords": kws,
            "suggested": sugg,
            "sigA": [v for v, _ in kw_top[:3]],
        })
        print(f"Q{qid:2d} {query[:22]:<24} 建议: {sugg}")

    json.dump(suggestions, open("evaluation/gt_suggestions.json", "w"),
              ensure_ascii=False, indent=2)
    print("\n已存 evaluation/gt_suggestions.json")


if __name__ == "__main__":
    asyncio.run(main())
