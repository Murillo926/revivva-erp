from fastapi import FastAPI

from app.routes.user_routes import router as user_router
from app.config.settings import settings

app = FastAPI(
    title="Revivva ERP API",
    version="1.0.0"
)

app.include_router(user_router)


@app.get("/")
def home():
    return {
        "mensagem": f"Bem-vindo ao {settings.APP_NAME}!"
    }


@app.get("/health")
def health():
    return {
        "status": "online"
    }