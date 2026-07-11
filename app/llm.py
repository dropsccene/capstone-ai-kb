from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.LLM_API_KEY,base_url = settings.LLM_BASE_URL)


def call_llm(prompt:str) -> str:
    response = client.chat.completions.create(
        model = "deepseek-v4-flash",
        messages = [
            {"role":"user","content":prompt}
        ]
    )
    return response.choices[0].message.content