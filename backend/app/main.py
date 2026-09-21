from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import leads, search
from app.core.config import API_DESCRIPTION, API_TITLE, API_VERSION

app = FastAPI(title=API_TITLE, version=API_VERSION, description=API_DESCRIPTION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(leads.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
