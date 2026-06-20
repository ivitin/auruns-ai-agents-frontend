from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API Settings
    API_TITLE: str = "Industrial AI Agent - UNS"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_SHEET_ID: str = ""
    
    # LLM - Groq (Gratuito)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL_NAME: str = "llama-3.1-8b-instant"
    
    # HuggingFace (Fallback)
    HUGGINGFACE_API_KEY: Optional[str] = None
    HF_MODEL_NAME: str = "google/flan-t5-large"
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "industrial-ai-agent"
    
    # Vector Store
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    # Agent Settings
    MAX_ITERATIONS: int = 10
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 2048
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignora campos extras do .env
    }

settings = Settings()
