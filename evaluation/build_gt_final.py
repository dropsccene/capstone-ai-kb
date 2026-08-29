"""合成最终 ground_truth.json：42 条（v1 确认 33 条 + 终审判据 9 条）"""
import json

# v1 首批用户 ✅ 的 query id（relevant = v1 建议组，用户已见预览并确认）
V1_OK = [2, 3, 4, 5, 7, 10, 11, 13, 14, 18, 19, 20, 22, 24, 25, 26, 27, 28, 29,
         31, 33, 34, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48]
# v2/v3 终审用户 ✅（relevant = 判据指明的精确 chunk）
FINAL_PICK = {
    6: ["chunk_8_311"],    # knights.items() 字典遍历（tutorial 5.6）
    8: ["chunk_8_135"],    # break/continue/else（tutorial 4.4）
    15: ["chunk_8_296"],   # union/intersection/difference（tutorial 5.x sets）
    21: ["chunk_8_481"],   # import json / json.dumps 示例
    30: ["chunk_8_677"],   # next(it) StopIteration（tutorial 9.8 Iterators）
    43: ["chunk_9_335"],   # 嵌套作用域自由变量（闭包机制）
    44: ["chunk_9_1551"],  # @wrapper 函数变换（装饰器定义）
    49: ["chunk_9_78"],    # 2.3 Names (identifiers and keywords)
    50: ["chunk_9_1420"],  # SOFT KEYWORDS / KEYWORDS 列表
}

sugs = {s["id"]: s for s in json.load(open("evaluation/gt_suggestions.json"))}

cases = []
for qid in V1_OK:
    cases.append({
        "id": qid,
        "question": sugs[qid]["question"],
        "relevant_chunks": sugs[qid]["suggested"],
    })
for qid, chunks in FINAL_PICK.items():
    # v2 表里没有 question，从 v1 表取（v2/v3 都是补对应 qid）
    cases.append({
        "id": qid,
        "question": sugs[qid]["question"],
        "relevant_chunks": chunks,
    })

cases.sort(key=lambda c: c["id"])
gt = {
    "description": f"Ground truth for Recall@K evaluation - {len(cases)} test cases (Python 3.14 docs: tutorial+reference, 2026-08-28)",
    "test_cases": cases,
}
json.dump(gt, open("evaluation/ground_truth.json", "w"), ensure_ascii=False, indent=2)
print(f"已写入 ground_truth.json：{len(cases)} 条")

# 老文件备份提醒
print("旧 results.json/results_rerank.json 仍是旧语料口径，评测时会被覆盖，无碍。")
