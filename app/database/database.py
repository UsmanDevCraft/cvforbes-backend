from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.config import DATABASE_URL, DATABASE_NAME
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
