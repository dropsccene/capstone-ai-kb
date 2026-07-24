from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


async def call_llm(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


async def call_llm_stream(prompt: str):
    stream = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        stream=True
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content is None:
            continue
        yield chunk.choices[0].delta.content
