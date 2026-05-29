from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from .database import engine
from .api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(title="Transio Server", lifespan=lifespan)

app.include_router(api_router)