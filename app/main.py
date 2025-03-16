from fastapi import FastAPI

from app.presentation.routes import router

app = FastAPI()
app.include_router(router)
