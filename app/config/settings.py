from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY:str
    PINECONE_API_KEY:str
#Pinecone config
    PINECONE_INDEX_NAME:str = "rag-pipeline"

#RAG parameters
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_BATCH_SIZE: int = 100
    TOP_K: int = 5
    MAX_TOKENS: int = 500
    MAX_FILE_SIZE_MB: int = 50
    
#Model Names
    EMBEDDING_MODEL:str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"
    
    model_config=SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
app_settings = Settings()