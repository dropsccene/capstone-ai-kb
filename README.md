# AI 知识库问答系统 — RAG + JWT + NL2SQL Agent

> 上传 PDF → 自然语言提问 → LLM 流式回答 + 引用来源。附带 JWT 认证体系和自然语言查数据库 Agent。

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green)](https://fastapi.tiangolo.com/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_V4-orange)](https://platform.deepseek.com/)
[![tests](https://img.shields.io/badge/tests-13/13_passed-brightgreen)]()
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)]()

---

## 特性

| 模块 | 功能 |
|------|------|
| 文档上传 | PDF 上传 → 提取文本 → 切片 → SentenceTransformers 向量化 → ChromaDB 持久化，一步完成 |
| 流式问答 | SSE 逐 token 实时推送（StreamingResponse），第一个字即刻出现 |
| 引用来源 | 每个回答附带检索到的原文片段，可溯源验证 |
| 知识库隔离 | 不同 PDF 存不同 ChromaDB collection（kb_1 / kb_2），互不干扰 |
| JWT 认证 | bcrypt 密码哈希 + JWT 签发/验证 + OAuth2PasswordBearer，/me 鉴权 |
| NL2SQL Agent | 自然语言查数据库——ReAct 循环 + Function Calling，自动生成 SQL → 执行 → 返回结果 |
| Docker | docker compose up 一键启动 PostgreSQL 16 + FastAPI，自动 Alembic 迁移 |

---

## 项目结构

```
capstone-ai-kb/
├── app/
│   ├── main.py              # FastAPI 入口 + lifespan + 注册 4 个 router
│   ├── config.py            # pydantic-settings 配置（DB / LLM / SECRET_KEY）
│   ├── database.py          # engine + SessionLocal + get_db（try/yield/finally）
│   ├── models.py            # ORM（User / KnowledgeBase / Document / Chunk）
│   ├── schemas.py           # Pydantic Schema（UserCreate/Login/Response/TokenResponse）
│   ├── auth.py              # get_current_user（OAuth2 + jwt.decode + db query）
│   ├── llm.py               # LLM 调用封装（call_llm + call_llm_stream）
│   ├── agent.py             # ReActAgent 类（tool_map + call_tool + run 循环）
│   ├── vector_store.py      # ChromaDB 向量存储 + SentenceTransformers Embedding
│   └── routers/
│       ├── documents.py     # POST /upload（PDF→文本→切片→Embedding→入库）
│       ├── asks.py          # POST /ask + /ask-stream（RAG 问答，非流式+SSE流式）
│       ├── auth.py          # POST /register + /login + GET /me（JWT 认证）
│       └── agent.py         # POST /ask-database（NL2SQL ReAct Agent）
├── tests/
│   ├── conftest.py          # pytest fixture + TestClient + create_test_token
│   ├── test_upload.py       # 3 条（上传 PDF / 非 PDF / chunk 计数）
│   ├── test_ask.py          # 1 条（RAG 问答 mock LLM + VectorStore）
│   ├── test_auth.py         # 7 条（注册/重复/弱密码/登录错密/登录/me/未授权）
│   └── test_agent.py        # 2 条（查数据库 / 缺参数 422）
├── alembic/                 # 数据库迁移（替代 create_all）
├── alembic.ini
├── Dockerfile               # 分层缓存 + ENTRYPOINT
├── docker-compose.yml       # PostgreSQL 16 + FastAPI 双容器
├── docker-entrypoint.sh     # 启动时自动 alembic upgrade head
├── .dockerignore
├── .env.example
├── requirements.txt
└── README.md
```

---

## 快速开始

### 本地运行（SQLite，零配置）

```bash
git clone https://github.com/dropsccene/capstone-ai-kb.git
cd capstone-ai-kb

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建 .env
echo 'DEEPSEEK_API_KEY=sk-your-key' > .env
echo 'BASE_URL=https://api.deepseek.com/v1' >> .env
echo 'SECRET_KEY=your-secret-key' >> .env

uvicorn app.main:app --reload
```

打开 http://localhost:8000/docs

### Docker 部署（PostgreSQL）

```bash
cp .env.example .env   # 填好 DEEPSEEK_API_KEY 和 SECRET_KEY
docker compose up -d   # PostgreSQL 16 + FastAPI，自动 Alembic 迁移
```

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 | 无（必填） |
| BASE_URL | LLM API 地址 | 无（必填） |
| SECRET_KEY | JWT 签名密钥 | 无（必填，secrets.token_hex(32) 生成） |
| DATABASE_URL | 数据库连接 | sqlite:///./capstone_kb.db |
| ALEMBIC_AUTO_MIGRATE | Docker 启动自动迁移 | true |

---

## API 端点

### 认证

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 注册（bcrypt 哈希密码） | 无 |
| POST | /api/auth/login | 登录 → 返回 JWT token | 无 |
| GET | /api/auth/me | 获取当前用户信息 | Bearer Token |

### 知识库

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /knowledge-bases/{kb_id}/upload | 上传 PDF → 切片 → 向量化 → 入库 |
| POST | /knowledge-bases/{kb_id}/ask | RAG 问答（非流式，返回 JSON） |
| POST | /knowledge-bases/{kb_id}/ask-stream | RAG 问答（SSE 流式，逐字返回） |

### NL2SQL Agent

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/agent/ask-database | 自然语言查数据库（ReAct + SQL 生成） |

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |

---

## 测试

```bash
pytest -v   # 13 passed, 0 failed
```

| 文件 | 条数 | 覆盖 |
|------|------|------|
| test_auth.py | 7 | register / 重复注册 / 登录错密码 / 登录 / me / 未授权 |
| test_upload.py | 3 | 上传 PDF / 非 PDF 422 / chunk 计数 |
| test_agent.py | 2 | NL2SQL 查询 / 缺参数 422 |
| test_ask.py | 1 | RAG 问答（mock LLM + VectorStore） |

Mock 策略：LLM 调用、VectorStore 全部 mock，0 网络请求、0 API 费用。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI 0.139 | lifespan + APIRouter + Depends |
| 数据库 | SQLite / PostgreSQL 16 | DATABASE_URL 一行切换 |
| ORM | SQLAlchemy 2.0 | declarative_base + sessionmaker |
| 迁移 | Alembic | autogenerate + upgrade/downgrade |
| 认证 | bcrypt + python-jose (JWT) | OAuth2PasswordBearer + HS256 |
| 向量库 | ChromaDB（PersistentClient） | 按 kb_id 隔离 collection |
| Embedding | SentenceTransformers | all-MiniLM-L6-v2，本地免联网 |
| LLM | DeepSeek V4 Flash | openai SDK，同步 + 流式 SSE |
| PDF | PyPDF2 3.0 | PdfReader(BytesIO(raw)) |
| Agent | ReAct + Function Calling | 自然语言 → SQL → 执行 → 返回 |
| 重试 | tenacity | @retry 装饰器，指数退避 |
| 校验 | Pydantic v2 + pydantic-settings | BaseSettings 读 .env |
| 测试 | pytest 9.1 | 13 条全绿 + unittest.mock |
| 容器 | Docker Compose | PostgreSQL + FastAPI + auto-migrate |

---

## 设计决策

> 每个技术选型都有理由，面试能讲清楚为什么这么选。

### 向量库选型：ChromaDB

我的项目中的向量库选用了 ChromaDB，因为 MVP 阶段要快——ChromaDB 嵌入式、零配置、Python 原生、支持持久化（PersistentClient），像 SQLite 一样即开即用。它的缺点也很明确：单机嵌入式，不支持分布式，扛不住大规模和高并发。如果后续上规模，可以换 Milvus（分布式自部署）或 pgvector（复用 PostgreSQL 运维，不用多维护一套向量库）。选型依据：团队是否已有 PostgreSQL → 有就用 pgvector，没有就上 Milvus。

### chunk_size 怎么定

chunk_size 定为 300——这是 RAG 常见的 200-500 范围中取的一个平衡值。如果太小（如 100），一句话容易被切碎导致语义不完整，检索命中不准；如果太大（如 1000），一个 chunk 里塞太多内容，召回的 chunk 中大部分内容与问题无关，额外消耗 token。MVP 阶段我没做严格的检索质量对比实验，主要靠人工抽样看检索结果是否合理。上生产要做 chunk_size 调优：固定一批测试问题，对比不同 chunk_size 的检索命中率，挑最优。同时配合 overlap=30 防止一句话正好被切断在 chunk 边界——保留最后 30 个字符与下一块重叠。

### top_k 为什么是 3

top_k=3 是内容平衡的选择。太小（top_k=1）容易跑偏，只拿一个 chunk 万一没命中或片面，回答就不完整；太大（top_k=10）拿太多无关 chunk 添加噪音，干扰 LLM 判断。top_k 跟 chunk_size 是关联的：chunk_size 大，单个 chunk 信息多，top_k 可以小；chunk_size 小，单个 chunk 信息少，top_k 要大才能覆盖。chunk_size=300 配 top_k=3，是配套的参数组合。上生产可以利用 rerank 技术，先粗检索 top_k=10，再用 reranker 模型重排取前 3，进一步提升检索精度。

### 同步 vs async：为什么端点用 def 而不是 async def

我的 /ask 和 /ask-stream 端点用的是 def（同步端点），没有用 async def。原因：当前 LLM 调用走的是 openai 同步 SDK（client.chat.completions.create），如果端点写 async def，这个同步阻塞调用会卡住 FastAPI 的事件循环——单条车道被 LLM 的几秒网络等待堵死，其他请求排队。

修法有两种：① 端点改 def，FastAPI 自动把同步端点扔进线程池跑，不阻塞事件循环（MVP 选这个，0 行逻辑变动）；② 端点保留 async def + 换 AsyncOpenAI 异步 SDK，真异步不阻塞，但改动更大。

MVP 阶段选方案①——简单够用。上生产切方案②配合 httpx.AsyncClient 连接池，或用 Celery 把 LLM 调用异步任务化，配合 Redis 做结果临时缓存。选型依据：QPS 和延迟要求。

### 为什么默认 SQLite 而不是 PostgreSQL

MVP 默认 SQLite 是因为零配置——不需要装数据库、不需要启动服务、新人 clone 下来 pip install -r requirements.txt && uvicorn app.main:app 就能跑。DATABASE_URL 在 config.py 里一行默认值，需要 PostgreSQL 时设环境变量覆盖即可，代码完全不动。选型逻辑：先降低上手门槛，再切生产数据库——不是偷懒，是有意设计的渐进路径。

### Alembic 替代 create_all

项目初期用 Base.metadata.create_all() 快速启动——lifespan 里一行建表，零配置。切 Alembic 后支持版本化迁移：每次改模型生成迁移文件，可回滚、可追溯、可团队协作。docker-entrypoint.sh 在容器启动时自动跑 alembic upgrade head，本地开发手动跑。选型逻辑：MVP 阶段 create_all 够快，上生产必须 Alembic——数据库 schema 变更没有版本控制就是定时炸弹。
---

## License

MIT
