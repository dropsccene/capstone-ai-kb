"""capstone-ai-kb 的 Locust 压测脚本。

跑法（在 WSL 里，服务先跑起来）：
    venv/bin/python -m uvicorn app.main:app --port 8000 &

    # 交互模式：浏览器开 http://localhost:8089 填并发数
    venv/bin/locust -f locustfile.py --host http://localhost:8000
    # 无人值守模式（-u 用户数 / -r 每秒启动数 / -t 时长）：
    venv/bin/locust -f locustfile.py --host http://localhost:8000 \
        --headless -u 5 -r 1 -t 3m --csv=rag_test --html=rag_report.html

本脚本压三个真实接口：
    /knowledge-bases/{kb_id}/ask            非流式 RAG 问答（有 IP 限流！）
    /knowledge-bases/{kb_id}/ask-stream     SSE 流式（无限流，另计首 token 时间）
    /api/agent/ask-database                 ReAct 数据库助手

已知注意点（对应代码里的行为，不是 bug）：
- /ask 的限流写死在 asks.py：5 次/分钟/IP。单机压它第 6 条起全是 429——
  压测前要认清：这代表"真实用户一个人每分钟也只能问 5 次"。真要压 /ask：
  停掉 Redis（rate_limit.py 对 Redis 不可用是放行/不拦的）或临时调大 max_req。
- /ask 缓存命中时 sources 是空数组（见 tests/test_ask.py 的 cache_hit 用例），
  所以断言只查 answer，不查 sources。
- 问题池别用同一句重复发——同一句会命中 Redis 缓存，测的是缓存不是系统。
"""
import random
import time

from locust import HttpUser, task, between, events

KB_ID = 1  # 改成你要压的知识库 id

# 真实问题池：基于知识库《毕业设计成果说明书》实际内容生成，覆盖文档各章节。
# 50 条不同问题 → 缓存 key（完整问题文本）几乎不重复，压测打的是真实 RAG 链路。
QUERY_POOL = [
    "这个项目是什么？",
    "项目名称是什么？",
    "这个应用支持哪些手势类型？",
    "如何识别单击（Tap）手势？",
    "长按手势是怎么实现和检测的？",
    "双击手势的检测逻辑是什么？",
    "左右滑动手势如何识别？",
    "双指缩放（Pinch Zoom）是怎么实现的？",
    "项目使用什么数据库存储数据？",
    "Room 数据库提供了哪些操作方法？",
    "数据库操作为什么用单线程 ExecutorService？",
    "手势识别区域如何处理滑动冲突？",
    "项目的整体架构是怎么设计的？",
    "Fragment 模块之间是如何解耦的？",
    "首页界面的主题风格是什么？",
    "首页标题和提示文字是什么内容？",
    "播放列表管理是如何实现的？",
    "播放器的循环播放逻辑是什么？",
    "图片画廊模块支持哪些操作？",
    "画廊的图片缩放是怎么实现的？",
    "触摸轨迹是怎么绘制和显示的？",
    "TouchTrailView 的绘制性能如何优化？",
    "项目对帧率有什么要求？",
    "手势识别事件如何持久化记录？",
    "历史记录支持哪些管理操作？",
    "项目的兼容性要求是什么？",
    "项目支持的最低 Android 版本是多少？",
    "手势冲突是如何处理的？",
    "项目采用什么设计模式？",
    "数据库使用了什么单例模式？",
    "手势检测封装模块的设计思路是什么？",
    "应用的导航架构是怎样的？",
    "项目的开发环境是什么？",
    "项目用到了哪些依赖库？",
    "需求分析阶段的主要功能有哪些？",
    "系统的业务流程图是怎样的？",
    "数据库的表结构如何设计？",
    "类图设计中核心类有哪些？",
    "手势识别引擎的实现原理是什么？",
    "软件测试都测试了哪些方面？",
    "测试执行结果如何？",
    "项目的创新点在哪里？",
    "与同类应用相比本项目有什么特色？",
    "项目的技术实现有哪些亮点？",
    "项目在性能与功耗上做了哪些优化？",
    "为什么避免在 onDraw 中创建短生命周期对象？",
    "应用的生命周期管理遵循什么规范？",
    "手势识别与界面更新如何解耦？",
    "本项目的研究背景是什么？",
    "手势交互相比传统按钮交互有什么优势？",
]

# ReAct 智能体是"SQLite 数据库查询助手"，问题池必须和它的任务域匹配——
# 拿文档问答问题喂它，它会反复试 SQL 直到 max_rounds=10 耗尽（实测 20s+ 超时）。
# 基于真实表结构（users/knowledge_bases/documents/chunks）生成的 DB 问题。
AGENT_QUERY_POOL = [
    "数据库里有哪些表？",
    "users 表里有多少条记录？",
    "每个用户的用户名和邮箱是什么？",
    "一共有几个知识库？",
    "documents 表里有哪些文档？",
    "最近上传的文档是什么？",
    "chunks 表有多少条记录？",
    "有哪些用户注册了？",
    "每个文档的文件大小是多少？",
    "knowledge_bases 表的 id 和名字是什么？",
    "数据库里有哪些文档文件名？",
    "文档的总字节数是多少？",
]


class RagUser(HttpUser):
    # 真人"读完答案再问下一个"的间隔。RAG 场景 RPS 天然低，这才是真实节奏
    wait_time = between(5, 15)

    def _pick(self):
        return {"question": random.choice(QUERY_POOL)}

    @task(2)
    def ask_rag(self):
        """非流式 RAG 问答——命中限流 5/min/IP 时会刷 429"""
        with self.client.post(
            f"/knowledge-bases/{KB_ID}/ask",
            json=self._pick(),
            catch_response=True,
            name="/ask (非流式)",
        ) as resp:
            if resp.status_code == 429:
                resp.failure("429 限流（RATE_LIMIT_MAX_REQ，压测时调大这个环境变量）")
                return
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            data = resp.json()
            # 业务断言：answer 要有内容；sources 允许为空（缓存命中时就是这样）
            if not data.get("answer") or len(data["answer"]) < 2:
                resp.failure("answer 为空")

    @task(2)
    def ask_stream(self):
        """SSE 流式——没有限流，另外单独统计首 token 时间（TTFT）"""
        t0 = time.perf_counter()
        with self.client.post(
            f"/knowledge-bases/{KB_ID}/ask-stream",
            json=self._pick(),
            stream=True,
            catch_response=True,
            name="/ask-stream (SSE)",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            got_data = False
            for line in resp.iter_lines():
                if not line or not line.startswith(b"data:"):
                    continue
                if not got_data:
                    # 第一个 data 块到达 = 用户等到的第一句话，这才是流式的核心指标
                    ttft_ms = (time.perf_counter() - t0) * 1000
                    events.request.fire(
                        request_type="TTFT",
                        name="/ask-stream 首token",
                        response_time=ttft_ms,
                        response_length=0,
                        context={},
                        exception=None,
                    )
                    got_data = True
                if line == b"data: [DONE]":
                    break
            if not got_data:
                resp.failure("流结束了但一个数据块都没收到")

    @task(1)
    def ask_agent(self):
        """ReAct 数据库助手——问题必须用 DB 问题池，见 AGENT_QUERY_POOL 注释"""
        with self.client.post(
            "/api/agent/ask-database",
            json={"question": random.choice(AGENT_QUERY_POOL)},
            catch_response=True,
            name="/api/agent/ask-database (ReAct)",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            data = resp.json()
            answer = data.get("answer")
            if isinstance(answer, dict) and "error" in answer:
                resp.failure("ReAct 达到最大轮数没答出来")
