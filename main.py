from ipaddress import ip_address

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

app = FastAPI(title="Contacts API", version="1.0")

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
#     user_agent = request.headers.get("user-agent")
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response


app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get("/")
def root():
    return {"message": "Contacts Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if not result.fetchone():
            raise HTTPException(status_code=500, detail="Database misconfigured")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB connection error")
