# Locust 压测 RAG 系统：发现、修复与复测全记录

> 日期：2026-08-05 ｜ 项目：capstone-ai-kb（FastAPI + ChromaDB + DeepSeek + 硅基流动 embedding + Redis）
> 工具：Locust 2.46.3 ｜ 压测脚本：`locustfile.py` ｜ 原始报告：`rag_test.csv` / `rag_test.html` / `rag_final.csv` / `rag_final.html`

## 一、背景与目标

对 RAG 服务的三个真实接口做负载测试，验证系统在 5 并发用户下的表现：

| 接口 | 类型 | 特点 |
|---|---|---|
| `POST /knowledge-bases/{kb_id}/ask` | 非流式 RAG 问答 | Redis 缓存 + IP 限流 |
| `POST /knowledge-bases/{kb_id}/ask-stream` | SSE 流式问答 | 无限流，核心指标是首 token 时间（TTFT） |
| `POST /api/agent/ask-database` | ReAct 智能体 | 多轮 LLM 调用 + SQL 工具执行 |

**关键设计**：RAG 场景是"低并发、单请求慢（秒级）、有思考间隔"，所以：
- 用户 think time 用 `between(5, 15)` 秒模拟真人读答案的间隔
- 问题池 50 条真实问题（基于知识库《毕业设计成果说明书》内容生成）——**同一句问题会命中 Redis 缓存，压测测的是缓存不是系统**
- 业务级断言：HTTP 200 不算成功，answer 为空/过短算失败
- SSE 接口单独统计首 token 时间（Locust 默认记的是请求完成时间，对流式是假象）

## 二、基线数据（改前，5 用户 ~60s）

| 指标 | 数值 | 解读 |
|---|---|---|
| 总请求 / 失败 | 40 / 10（25%） | 失败全部是 429 |
| `/ask` 失败率 | **66.7%**（10/15 全是 429） | 限流 5 次/分钟/IP 硬编码在 asks.py，单机压测第 5 条就触发 |
| `/ask` P50 | **4ms** | 假象：问题池只有 10 句，大量命中 Redis 缓存 |
| ReAct P50 / P95 | 5.3s / **12s** | 最慢接口：多轮 LLM + 同步 SQL |
| TTFT P50 / P95 | 1.5s / 5.1s | 并发下首 token 变慢 3 倍 |

**三个基线发现**：
1. 限流参数写死（`max_req=5` 覆盖了 rate_limit.py 本就支持的 `RATE_LIMIT_MAX_REQ` 配置）
2. `/ask` 的 P50 4ms 是缓存命中率污染（问题池太小 + 缓存 key=完整问题文本）
3. ReAct 的 `query_database` 是同步 SQL，阻塞 FastAPI 事件循环

## 三、修复（三步）

### 1. 限流可配置化（asks.py）
```python
# 之前：硬编码，配置被压住
if not check_rate_limit(request.client.host, max_req=5, window_sec=60):
# 之后：读环境变量，默认 5 兜底，压测/运维可调
max_req = int(os.getenv("RATE_LIMIT_MAX_REQ", "5"))
```
> 小发现：`.env` 里本来就配了 `RATE_LIMIT_MAX_REQ=60`，硬编码把它压成了 5。修复后生产行为回到配置值 60/分钟，这才是配置的本意。

### 2. 问题池扩到 50 条真实问题（locustfile.py）
基于知识库实际内容生成，覆盖文档各章节（手势类型、数据库设计、性能优化……）。
同时给 ReAct 智能体配了独立的 DB 问题池（见第四节"控制变量事故"）。

### 3. ReAct 同步 SQL 异步化（agent.py）
```python
# 之前：同步调用阻塞事件循环
result = self.tool_map[tc.function.name](**body)
# 之后：丢线程池执行
result = await asyncio.to_thread(self.tool_map[tc.function.name], **body)
```
> 工程决策：用 `asyncio.to_thread` 轻量止血（保持数据库层不动），而非全面改 async engine——渐进式改造，风险可控。

**测试验证**：`pytest` 17 passed（限流测试钉住 `RATE_LIMIT_MAX_REQ=5` 后与 .env 解耦）。

## 四、控制变量事故（本实验最大的教学点）

第一轮复测 ReAct 反而恶化：P50 5.3s → 16s，且 3/9 请求（33%）报"达到最大轮数"（20s+ 超时）。

**原因**：新问题池是"文档问答"问题（"这个项目是什么？"），但 ReAct 是 SQLite 数据库查询助手——文档问题它查不到，只能反复试 SQL 直到 10 轮耗尽。

**教训**：对比实验必须控制变量。基线的问题池恰好都是 DB 问题，改问题池的同时改了问题域，两个变量混在一起，ReAct 的前后对比无效。修复：给 ReAct 任务配专属 DB 问题池（基于真实表结构 users/knowledge_bases/documents/chunks 生成 12 条）。

> 博客视角：这是"压测脚本本身也是被测对象"的典型坑——压测负载不合适，测出来的不是系统性能。

## 五、修复后数据

### 复测 1（5 用户 3 分钟，缓存跨轮变热）
| 指标 | 数值 | 对比基线 |
|---|---|---|
| 总失败率 | **0%**（91 reqs） | 25% → 0% ✅ |
| `/ask` 失败率 | 0%（0 个 429） | 66.7% → 0% ✅ |
| ReAct | 13 reqs 0 fails，P50 5.6s | 5.3s（无显著变化，见"负结果"） |
| TTFT P50 | 1.8s | 1.5s（抖动范围） |

### 复测 2（3 用户 90 秒，Redis 缓存清零——真实链路延迟）
| 指标 | 数值 | 说明 |
|---|---|---|
| `/ask` P50 / P90 | **2.8s / 6.2s** | 这才是真实 RAG 延迟（embedding + 检索 + LLM） |
| ReAct | 4 reqs 0 fails，P50 5.3s，Max 5.7s | 无 20s 超时 |
| TTFT P50 | 2.2s | — |
| TTFT 尾部 | P95 14s（n=7，单离群） | 外部 LLM API 抖动主导 |

## 六、前后对比总表

| 指标 | 基线 | 修复后 | 结论 |
|---|---|---|---|
| 总失败率 | 25% | **0%** | ✅ 可量化改进 |
| `/ask` 429 失败率 | 66.7% | **0%** | ✅ 限流可配置化 |
| `/ask` P50 | 4ms（缓存假象） | **2.8s（真实链路）** | 之前测不到真实延迟 |
| ReAct P95 | 12s | 5.7~11s（轮次波动） | ⚠️ 见负结果 |
| TTFT P50 | 1.5s | 1.8~2.2s | 抖动范围内 |
| TTFT P95 | 5.1s | 2.4s~14s（轮间波动大） | LLM 外部抖动主导 |

## 七、诚实的负结果（比正结果更有价值）

**`asyncio.to_thread` 在 5 用户下没有带来 ReAct 延迟改善**（P95 12s → 11s，基本持平）。

原因分析：ReAct 的延迟构成 = 多轮 LLM 调用（每轮 2~4s，DB 问题约 2 轮）≫ 本地 SQL 执行（毫秒级）。**瓶颈在外部 LLM 调用本身，不在本地同步代码**。同步 SQL 阻塞事件循环的危害要在更高并发下才显形（事件循环饥饿：一个请求的 SQL 挡住所有人）。

**这恰好是面试/博客要的"预期 vs 实际"故事**：修复前先写假设（"同步 SQL 是 P95 12s 的主因"），修复后拿数据证伪/修正（"主因是 LLM 多轮调用"）——数据驱动，而不是改完就吹。

## 八、下一步假设（未验证）

1. **加压验证 to_thread 收益**：20~50 用户下事件循环饥饿是否显形（ReAct P95 是否随并发变差）
2. **mock LLM 长时浸泡测试**：把 `LLM_BASE_URL` 指向本地假 LLM（固定延迟），分离"你自己的系统瓶颈"和"外部 API 延迟"
3. **VectorStore 每请求新建 chromadb.PersistentClient**（本次未动）：SQLite 文件反复打开，高并发下锁竞争——本地最可疑的瓶颈
4. **ReAct 轮数优化**：max_rounds=10 上限太高，文档类问题会跑 20s+ 才放弃

## 九、复现方法

```bash
# 1. 启动服务（压测时调大限流，排除干扰变量）
cd ~/capstone-ai-kb
RATE_LIMIT_MAX_REQ=1000 nohup venv/bin/python -m uvicorn app.main:app --port 8000 &

# 2. 压测前清空缓存（测真实链路）
venv/bin/python -c "import redis; r=redis.Redis(host='localhost',port=6379,decode_responses=True); [r.delete(k) for k in r.keys('ask:*')]"

# 3. 跑压测
venv/bin/locust -f locustfile.py --host http://localhost:8000 --headless -u 5 -r 1 -t 3m --csv=rag_test --html=rag_report.html
```
