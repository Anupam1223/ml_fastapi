from fastapi import FastAPI

from app.presentation.routes import router as api_router
from app.presentation.websockets import router as ws_router

app = FastAPI()
app.include_router(api_router)
app.include_router(ws_router, prefix="")