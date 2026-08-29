"""第二批建议标注：17 条「无」的 query，用人工指定关键词做包含匹配（独立信号）"""
import re
import chromadb

col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
data = col.get(include=['documents'])
ids, docs = data['ids'], data['documents']

# 人工指定关键词（基于 Python 文档章节知识；多关键词组合提升精度）
MANUAL = {
    1: ["interactive mode", "exit()", "quit()"],
    6: ["looping over", "dictionaries"],
    8: ["break and continue"],
    9: ["match statement", "case"],
    12: ["list comprehension"],
    15: ["set", "union", "intersection"],
    16: ["import statement", "importlib"],
    17: ["module search path"],
    21: ["json.dump", "json.load"],
    23: ["catching", "exceptions", "except"],
    30: ["iterator protocol"],
    32: ["yield", "generator"],
    35: ["pathlib", "os.path"],
    43: ["closure", "nested"],
    44: ["decorator", "wrapper"],
    49: ["identifier", "letter"],
    50: ["keyword", "soft keyword"],
}

out = []
for qid, kws in MANUAL.items():
    def score(doc: str) -> int:
        low = doc.lower()
        return sum(1 for k in kws if k.lower() in low)

    ranked = sorted(((score(d), i) for i, d in enumerate(docs)), reverse=True)
    hits = [(ids[i], s) for s, i in ranked if s > 0]
    out.append({"id": qid, "keywords": kws, "suggested": [h[0] for h in hits[:3]],
                "sig_count": [h[1] for h in hits[:3]]})
    print(f"Q{qid:2d} {kws} -> {out[-1]['suggested']}")

import json
json.dump(out, open('evaluation/gt_suggestions_v2.json', 'w'), ensure_ascii=False, indent=2)

# 渲染复核表
lines = ['# Ground Truth 建议标注 v2（17 条待复核）', '']
for s in out:
    lines.append(f'**Q{s["id"]}.** 关键词 {s["keywords"]}')
    for vid in s['suggested']:
        # 查原文
        preview = ''
        for i, d in enumerate(docs):
            if ids[i] == vid:
                preview = d[:110].replace('\n', ' | ')
                break
        lines.append(f'- {vid}：{preview}')
    lines.append('')
open('evaluation/gt_suggestions_v2.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('已存 gt_suggestions_v2.json / .md')
