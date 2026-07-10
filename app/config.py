from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL:str = "sqlite:///./capstone_kb.db"
    LLM_API_KEY:str = ""
    LLM_BASE_URL:str = "https://api.deepseek.com"

settings = Settings()