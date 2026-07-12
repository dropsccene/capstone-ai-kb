# AI 知识库问答系统（RAG + Streaming）

> 上传 PDF，像问人一样向文档自由提问——LLM 流式回答 + 引用来源。

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green)](https://fastapi.tiangolo.com/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-orange)](https://platform.deepseek.com/)

---

## ✨ 特性

- 📄 **PDF 上传自动处理**：上传 PDF → 提取文本 → 字符切片（overlap 防截断）→ Sentence Transformers 向量化 → ChromaDB 持久化，全过程一步完成
- 💬 **流式问答**：提出问题后 LLM 逐字实时生成答案（SSE），不等完整响应，第一个字即刻出现
- 📎 **引用来源**：每个回答附带检索到的原文片段，可溯源验证
- 🧠 **多知识库隔离**：不同 PDF 存入不同 collection（`kb_1`/`kb_2`/`kb_3`），互不干扰
- 🔒 **防幻觉约束**：当文档中无相关信息时，LLM 诚实回答"抱歉，我无法回答这个问题"

---

## 📁 项目结构

```
capstone-ai-kb/
├── app/
│   ├── main.py              # FastAPI 入口 + lifespan（启动自动 create_all 建表）
│   ├── config.py            # pydantic-settings 配置（DATABASE_URL / LLM key / base URL）
│   ├── database.py          # engine + SessionLocal + get_db（try/yield/finally）
│   ├── models.py            # SQLAlchemy ORM（KnowledgeBase / Document / Chunk）
│   ├── llm.py               # LLM 调用封装（call_llm 同步 + call_llm_stream 流式）
│   ├── vector_store.py      # ChromaDB 向量存储 + SentenceTransformers Embedding
│   └── routers/
│       ├── documents.py     # POST /upload 上传 + PDF 文本提取 + 切片 + 向量入库
│       └── asks.py          # POST /ask（非流式）+ /ask-stream（SSE 流式）RAG 问答
├── requirements.txt
├── docker-compose.yml       # PostgreSQL 16 + FastAPI 双容器
└── README.md
```

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- 有效的 DeepSeek API Key

### 本地运行（SQLite，零依赖开箱即跑）

```bash
# 1. 克隆项目
git clone https://github.com/dropsccene/capstone-ai-kb.git
cd capstone-ai-kb

# 2. 创建虚拟环境 + 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 创建 .env 文件（只需要这两项）
echo 'DEEPSEEK_API_KEY=sk-your-deepseek-key' > .env
echo 'BASE_URL=https://api.deepseek.com/v1' >> .env

# 4. 启动服务（默认 SQLite，无需装数据库）
uvicorn app.main:app --reload
```

打开 http://localhost:8000/docs 查看 Swagger 文档。

### 环境变量

所有配置在 `app/config.py` 中，通过 `.env` 文件或环境变量设置：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 无（必填） |
| `BASE_URL` | LLM API 地址 | 无（必填） |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./capstone_kb.db` |

> **为什么默认 SQLite？** MVP 阶段 SQLite 零配置开箱即用，不用装 PostgreSQL。需要 PostgreSQL 时（如 Docker 部署），设置 `DATABASE_URL=postgresql+psycopg2://...` 即可——一行配置切换，代码不动。

---

## 📡 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/knowledge-bases/{kb_id}/upload` | 上传 PDF（提取文本 → 切片 → Embedding → ChromaDB） |
| `POST` | `/knowledge-bases/{kb_id}/ask` | RAG 问答（非流式，一次性返回完整 JSON） |
| `POST` | `/knowledge-bases/{kb_id}/ask-stream` | RAG 问答（SSE 流式，逐字实时返回） |

### 使用示例

**上传 PDF：**

```bash
curl -X POST http://localhost:8000/knowledge-bases/1/upload \
  -F "file=@resume.pdf"
```

返回：
```json
{"doc_id": 1, "chunks": 94}
```

**流式问答：**

```bash
curl -N -X POST http://localhost:8000/knowledge-bases/1/ask-stream \
  -H "Content-Type: application/json" \
  -d '{"question": "这个人会什么技术栈？"}'
```

SSE 逐行输出（`-N` 关闭 curl 缓冲，否则看不出实时效果）：
```
data: 根据
data: 资料
data: ，这个人
data: 掌握
...
data: [DONE]
```

**非流式问答：**

```bash
curl -X POST http://localhost:8000/knowledge-bases/1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "项目用了哪些框架？"}'
```

返回：
```json
{
  "answer": "根据资料，项目使用了FastAPI、SQLAlchemy、ChromaDB...",
  "sources": ["原文片段1", "原文片段2", "原文片段3"]
}
```

---

## 🛠 技术栈

| 层级 | 技术选型 | 备注 |
|------|---------|------|
| Web 框架 | FastAPI 0.139 | lifespan 启动建表 |
| 数据库默认 | SQLite | 零配置开箱即用，`DATABASE_URL` 一行切 PostgreSQL |
| ORM | SQLAlchemy 2.0 | declarative_base + sessionmaker |
| 建表方式 | `Base.metadata.create_all()` | lifespan 中自动执行，无需 Alembic |
| 向量库 | ChromaDB（PersistentClient） | 嵌入式持久化，数据落盘 `./data/chroma/` |
| Embedding | Sentence Transformers（all-MiniLM-L6-v2） | 本地运行，`local_files_only=True` 免联网 |
| LLM | DeepSeek V4 Flash | openai SDK 调用（同步 + 流式 `stream=True`） |
| 流式协议 | SSE（Server-Sent Events） | `StreamingResponse` + `media_type="text/event-stream"` |
| PDF 解析 | PyPDF2 3.0 | `PdfReader(BytesIO(raw))` |
| 数据校验 | Pydantic v2 + pydantic-settings | `BaseSettings` 读 `.env` |

---

## 📐 设计决策

> 每个技术选型都有理由，面试能讲清楚为什么这么选。

### 向量库选型：ChromaDB

我的项目中的向量库选用了 ChromaDB，因为 MVP 阶段要快——ChromaDB 嵌入式、零配置、Python 原生、支持持久化（PersistentClient），像 SQLite 一样即开即用。它的缺点也很明确：单机嵌入式，不支持分布式，扛不住大规模和高并发。如果后续上规模，可以换 Milvus（分布式自部署）或 pgvector（复用 PostgreSQL 运维，不用多维护一套向量库）。选型依据：团队是否已有 PostgreSQL → 有就用 pgvector，没有就上 Milvus。

### chunk_size 怎么定

chunk_size 定为 300——这是 RAG 常见的 200-500 范围中取的一个平衡值。如果太小（如 100），一句话容易被切碎导致语义不完整，检索命中不准；如果太大（如 1000），一个 chunk 里塞太多内容，召回的 chunk 中大部分内容与问题无关，额外消耗 token。MVP 阶段我没做严格的检索质量对比实验，主要靠人工抽样看检索结果是否合理。上生产要做 chunk_size 调优：固定一批测试问题，对比不同 chunk_size 的检索命中率，挑最优。同时配合 overlap=30 防止一句话正好被切断在 chunk 边界——保留最后 30 个字符与下一块重叠。

### top_k 为什么是 3

top_k=3 是内容平衡的选择。太小（top_k=1）容易跑偏，只拿一个 chunk 万一没命中或片面，回答就不完整；太大（top_k=10）拿太多无关 chunk 添加噪音，干扰 LLM 判断。top_k 跟 chunk_size 是关联的：chunk_size 大，单个 chunk 信息多，top_k 可以小；chunk_size 小，单个 chunk 信息少，top_k 要大才能覆盖。chunk_size=300 配 top_k=3，是配套的参数组合。上生产可以利用 rerank 技术，先粗检索 top_k=10，再用 reranker 模型重排取前 3，进一步提升检索精度。

### 同步 vs async：为什么端点用 `def` 而不是 `async def`

我的 `/ask` 和 `/ask-stream` 端点用的是 `def`（同步端点），没有用 `async def`。原因：当前 LLM 调用走的是 openai 同步 SDK（`client.chat.completions.create`），如果端点写 `async def`，这个同步阻塞调用会卡住 FastAPI 的事件循环——单条车道被 LLM 的几秒网络等待堵死，其他请求排队。

修法有两种：① 端点改 `def`，FastAPI 自动把同步端点扔进线程池跑，不阻塞事件循环（MVP 选这个，0 行逻辑变动）；② 端点保留 `async def` + 换 `AsyncOpenAI` 异步 SDK，真异步不阻塞，但改动更大。

MVP 阶段选方案①——简单够用。上生产切方案②配合 `httpx.AsyncClient` 连接池，或用 Celery 把 LLM 调用异步任务化，配合 Redis 做结果临时缓存。选型依据：QPS 和延迟要求。

### 为什么默认 SQLite 而不是 PostgreSQL

MVP 默认 SQLite 是因为零配置——不需要装数据库、不需要启动服务、新人 clone 下来 `pip install -r requirements.txt && uvicorn app.main:app` 就能跑。`DATABASE_URL` 在 `config.py` 里一行默认值，需要 PostgreSQL 时设环境变量覆盖即可，代码完全不动。选型逻辑：先降低上手门槛，再切生产数据库——不是偷懒，是有意设计的渐进路径。

---

## 🔜 待做（方向清楚，按优先级）

- [ ] **Dockerfile** — 配好入口脚本 `docker-entrypoint.sh`（启动时自动 `create_all` 建表），`docker-compose up` 一键启动
- [ ] **Redis 缓存** — 高频问答缓存（相同问题不重复查向量库 + 调 LLM）
- [ ] **rerank 重排** — 粗检索 top_k=10 → reranker 重排取前 3，提升检索精度
- [ ] **pytest 测试** — 端点级测试覆盖 upload / ask / ask-stream
- [ ] **限流** — 滑动窗口 IP 频率限制，防滥用

---

## 📝 License

MIT

---

## 🙋‍♂️ 关于这个项目

这是我从 Python 基础开始自学 2 个月、独立完成的第一个 AI 后端项目。从 FastAPI 的 `/health` 端点写到 RAG 完整回路 + 流式问答，每一步都是自己写的。项目还有很多可优化的地方，方向清楚，持续迭代中。

**完整学习路径**：[python-ai-backend](https://github.com/dropsccene/python-ai-backend) — 从 Day 1 到 ReAct Agent 的完整学习记录（含 17 条 pytest 测试）。
