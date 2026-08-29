"""hit@K：答案区（任一 relevant chunk）进 top-K 的比例——跨 chunk 粒度公平可比"""
import json

rows = json.load(open('evaluation/results_rerank.json'))

for label, ret_key in [("RRF", "rrf_retrieved@10"), ("rerank", "reranked")]:
    print(f"== {label} ==")
    for k in (3, 5, 10):
        hits = sum(1 for r in rows if set(r['relevant']) & set(r[ret_key][:k]))
        print(f"  hit@{k}: {hits / len(rows):.3f}")
