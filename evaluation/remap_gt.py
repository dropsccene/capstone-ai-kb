"""标注重映射：600 字符新切片下，按文本重叠把旧答案 chunk 定位到新 chunk id

原理：旧 300 字符 chunk 的文本必然完整落在某个新 600 字符 chunk 内（切片同源、
清洗规则一致），取新 chunk 归一化文本包含「旧答案归一化文本前 120 字符」者为命中。
"""
import json
import re
import chromadb


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
data = col.get(include=['documents'])
new_docs = data['documents']
new_ids = data['ids']
new_norm = [norm(d) for d in new_docs]

answers = json.load(open('evaluation/gt_answer_texts.json'))

gt = {"description": f"Ground truth for Recall@K - {len(answers)} test cases (Python 3.14 docs, 600-char chunks, 2026-08-28)",
      "test_cases": []}

miss_total = 0
for case in answers:
    mapped = []
    for text in case['answer_texts']:
        probe = norm(text)[:120]
        hit = None
        for i, nd in enumerate(new_norm):
            if probe and probe in nd:
                hit = new_ids[i]
                break
        if hit and hit not in mapped:
            mapped.append(hit)
        elif not hit:
            miss_total += 1
            print(f"  ⚠️ Q{case['id']} 有一条答案文本未找到新 chunk（前60字符: {probe[:60]}）")
    gt['test_cases'].append({
        "id": case['id'],
        "question": case['question'],
        "relevant_chunks": mapped,
    })

json.dump(gt, open('evaluation/ground_truth.json', 'w'), ensure_ascii=False, indent=2)
n_multi = sum(1 for t in gt['test_cases'] if len(t['relevant_chunks']) > 1)
print(f"重映射完成：{len(gt['test_cases'])} 条 | 未命中 {miss_total} 条答案 | 多答案条目 {n_multi}")
