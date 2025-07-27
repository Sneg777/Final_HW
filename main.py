from ipaddress import ip_address
from pathlib import Path
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from src.database.db import get_db
from src.routes import contacts, auth, users
from fastapi_limiter import FastAPILimiter
from src.conf.config import config
from typing import Callable
from starlette.responses import JSONResponse
import re


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler for FastAPI application.
    Handles startup and shutdown events.
    """
    r = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)
    yield

    await r.close()


app = FastAPI(title="Contacts API",
              version="1.0",
              description="A REST API for managing contacts with authentication and rate limiting",
              lifespan=lifespan
              )

# banned_ips = [
#     ip_address("127.0.0.1"),
#     ip_address("::1"),
#     ip_address("244.178.44.111"),
#     ip_address("::1"),
#     ip_address("192.168.1.1"),
#     ip_address("192.168.1.2"),
#
# ]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)

# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     """
#     Middleware to block requests from banned IP addresses.
#
#     Args:
#         request: Incoming request
#         call_next: Next middleware/handler in chain
#
#     Returns:
#         JSONResponse: 403 Forbidden if IP is banned
#         Response: Normal response if IP is allowed
#     """
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response

# user_agent_ban_list = [r"Gecko", r"Python-urllib"]
#
#
# @app.middleware("http")
# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#     """
#     Middleware to block requests based on User-Agent header patterns.
#
#     Args:
#         request: Incoming request
#         call_next: Next middleware/handler in chain
#
#     Returns:
#         JSONResponse: 403 Forbidden if User-Agent matches banned pattern
#         Response: Normal response if User-Agent is allowed
#     """
#     user_agent = request.headers.get("user-agent")
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response
static_dir = Path("src/static")
if not static_dir.exists():
    static_dir.mkdir(parents=True)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: Simple welcome message
    """
    return {"message": "Contacts Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the application and database connection.

    Args:
        db (AsyncSession): Database session dependency

    Returns:
        dict: Success message if healthy

    Raises:
        HTTPException: 500 if database connection fails
    """
    try:
        result = await db.execute(text("SELECT 1"))
        if not result.fetchone():
            raise HTTPException(status_code=500, detail="Database misconfigured")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB connection error")
