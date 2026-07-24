from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from pymongo import AsyncMongoClient

from app.config import DATABASE_NAME, DATABASE_URL
from app.models.anonymous_user import AnonymousUser
from app.models.banned_ip import BannedIP
from app.models.generated_cv import GeneratedCV


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize PyMongo Async client
    client = AsyncMongoClient(DATABASE_URL)

    # Initialize Beanie with your models
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            AnonymousUser,
            BannedIP,
            GeneratedCV,
        ],
    )

    yield  # Server runs here

    # Clean up connection when shutting down
    client.close()
