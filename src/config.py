# config.py
from functools import lru_cache
from pydantic_settings import BaseSettings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings

# Ollama models: llama3.2, deepseek-r1:1.5b

class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: str | None = None
    model_temperature: float = 0.0
    auth_secret_key: str | None = None
    langchain_api_key: str | None = None
    langchain_tracing_v2: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class LLMConfig:
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def get_llm(self) -> BaseLanguageModel:
        if self.settings.environment == "production":
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be set in production environment")
            
            return ChatOpenAI(
                api_key=self.settings.openai_api_key,
                model="gpt-4o-mini",
                temperature=self.settings.model_temperature,
            )
        else:
            return ChatOllama(
                model="llama3.2",
                temperature=self.settings.model_temperature,
            )
    
    def get_embeddings(self) -> Embeddings:
        if self.settings.environment == "production":
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be set in production environment")
            
            return OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model="text-embedding-3-large"
            )
        else:
            return OllamaEmbeddings(
                model="llama3.2"
            )

def get_llm_config() -> LLMConfig:
    settings = get_settings()
    return LLMConfig(settings)