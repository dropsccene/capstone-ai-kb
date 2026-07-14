from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL:str = os.getenv("DATABASE_URL")
    LLM_API_KEY:str = os.getenv("DEEPSEEK_API_KEY")
    LLM_BASE_URL:str = os.getenv("BASE_URL")
    SECRET_KEY:str = "dev-secret-change-me"

settings = Settings()