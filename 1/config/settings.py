from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")

    # Embedding
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Knowledge base
    kb_collection_name: str = "ecommerce_kb"
    kb_persist_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
