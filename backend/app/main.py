from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine

app = FastAPI(title="School Management API", version="1.0.0")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
