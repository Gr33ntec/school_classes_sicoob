import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.database import engine
from app.core.errors import ConflictError, NotFoundError

app = FastAPI(title="School Management API", version="1.0.0")

CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ORIGINS", "http://localhost:8888,http://127.0.0.1:8888"
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(api_router)


@app.exception_handler(NotFoundError)
def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse({"detail": str(exc)}, status_code=404)


@app.exception_handler(ConflictError)
def conflict_handler(_: Request, exc: ConflictError):
    return JSONResponse({"detail": str(exc)}, status_code=409)


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
