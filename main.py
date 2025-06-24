from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import contacts

app = FastAPI(title="Contacts API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix="/api")


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
