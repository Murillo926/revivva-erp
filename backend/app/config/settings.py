from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    SECRET_KEY: str
    DATABASE_URL: str
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()