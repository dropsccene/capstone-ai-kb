"""把 gt_suggestions.json 渲染为人类可读复核表 gt_suggestions.md"""
import json
import chromadb

col = chromadb.PersistentClient(path='./data/chroma').get_collection('kb_1')
data = col.get(include=['documents'])
id_to_doc = dict(zip(data['ids'], data['documents']))
sugs = json.load(open('evaluation/gt_suggestions.json'))

lines = ['# Ground Truth 建议标注（待你复核）', '',
         '> 用法：逐条看「建议 chunk 的原文预览」，判断它是否**真的回答了**该问题。',
         '> 确认：每条后标注 ✅（建议的 chunk 之一就是答案）或 ✏️ 修改（写正确 chunk id 或「无」）。',
         '> 注意：标注应基于原文语义，不是「检索器给的」——若建议的 chunk 答非所问请换掉。', '']
for s in sugs:
    lines.append(f'**Q{s["id"]}.** {s["question"]}')
    for vid in s['suggested']:
        preview = id_to_doc.get(vid, '(缺失)')[:110].replace('\n', ' | ')
        lines.append(f'- {vid}：{preview}')
    lines.append('')

open('evaluation/gt_suggestions.md', 'w', encoding='utf-8').write('\n'.join(lines))
print(f'已生成 evaluation/gt_suggestions.md，共 {len(sugs)} 条')
