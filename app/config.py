from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LLM Webhook API"
    debug: bool = False

    LLM_API_KEY: str
    MODEL_LLM: str
    RABBITMQ_URL: str
    QUEUE_NAME: str
    TG_BOT: str
    CHAT_ID: str


settings = Settings()