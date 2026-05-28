from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routes import router as routes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(title="Transio Backend", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(routes_router)