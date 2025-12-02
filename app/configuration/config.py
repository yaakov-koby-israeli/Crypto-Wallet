from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM:  str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CHAIN_ID: int
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    model_config = {"env_file": ".env", "extra": "ignore"}
    GANACHE_URL: str

settings = Settings()


