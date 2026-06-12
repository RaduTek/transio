from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine
from .api import router as api_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(title="Transio Server", lifespan=lifespan)

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
