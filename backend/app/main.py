from fastapi import FastAPI

from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router
from app.routes.client_routes import router as client_router
from app.routes.product_routes import router as product_router
from app.routes.stock_routes import router as stock_router
from app.routes.seller_routes import router as seller_router
from app.routes.seller_stock_routes import router as seller_stock_router
from app.routes.sale_routes import router as sale_router

from app.config.settings import settings

app = FastAPI(
    title="Revivva ERP API",
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(client_router)
app.include_router(product_router)
app.include_router(stock_router)
app.include_router(seller_router)
app.include_router(seller_stock_router)
app.include_router(sale_router)

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