from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prepare the local environment automatically; no UI action is required.
    engine.seed_demo_data()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Decision-support software for transaction risk and AML investigation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": settings.app_name, "docs": "/docs"}
