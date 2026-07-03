from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.chatbot import get_bot


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"

app = FastAPI(
    title="SafeX FAQ Chatbot",
    description="A lightweight AI/ML FAQ assistant for SafeX public website content.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=600)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "project": "SafeX FAQ Chatbot"}


@app.get("/api/suggestions")
def suggestions() -> dict[str, list[str]]:
    return {"suggested_questions": get_bot().suggested_questions()}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    return get_bot().answer(request.message)
