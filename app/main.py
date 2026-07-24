from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.database.database import lifespan
from app.middleware.ip_guard import IPGuardMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routes.admin import router as admin_router
from app.routes.cv_generation import router as cv_generation_router

load_dotenv()

# Initialize the limiter (tracks users by their IP address)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI CV Tailor Engine API", lifespan=lifespan)

# Add the rate limit error handler to FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://cvforbes.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(IPGuardMiddleware)

app.include_router(cv_generation_router)
app.include_router(admin_router)
