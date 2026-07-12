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


def call_llm_stream(prompt:str):
    stream = client.chat.completions.create(
        model = "deepseek-v4-flash",
        messages = [{
            "role":"user",
            "content":prompt
        }],
        stream = True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is None :
            continue
        else:
            yield chunk.choices[0].delta.content

