from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3.5:9b"
    embedding_model: str = "nomic-embed-text"
    
    llm_num_predict: int = 2048  # max tokens to generate per response
    llm_num_ctx: int = 8192      # context window size (increased to fit more chunks + history)
    llm_think: bool = False      # disable Qwen3 chain-of-thought thinking mode

    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 8
    
    data_dir: Path = Path("data/documents")
    vector_store_dir: Path = Path("vector_store")
    
    class Config:
        env_file = ".env"

settings = Settings()
