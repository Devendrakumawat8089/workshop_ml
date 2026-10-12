from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import init_db
from ai_agent import ask_agent

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Dev Clinic AI Chatbot", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ChatRequest(BaseModel):
    message: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = await ask_agent(message)
        if isinstance(result, dict) and "answer" in result:
            return result
        return {"answer": str(result), "tools_used": []}
    except Exception as exc:
        logging.exception("Chatbot request failed")
        # Detailed error is logged server-side; client receives a safe message.
        raise HTTPException(
            status_code=502,
            detail=f"Chatbot backend failed: {type(exc).__name__}: {exc}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
