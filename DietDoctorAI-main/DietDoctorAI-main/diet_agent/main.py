import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.utils.context_utils import Aclosing
from google.genai import types
from pydantic import BaseModel

# Load .env from this package
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from diet_agent.agent import root_agent  # noqa: E402

APP_NAME = "diet_agent"

# Session storage: PostgreSQL if DATABASE_URL is set, else in-memory
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    _db_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "postgresql+asyncpg+asyncpg" in _db_url:
        _db_url = DATABASE_URL
    from google.adk.sessions import DatabaseSessionService
    print("🗄️  Using DatabaseSessionService (PostgreSQL)")
    session_service = DatabaseSessionService(db_url=_db_url)
else:
    from google.adk.sessions import InMemorySessionService
    print("⚠️  Using InMemorySessionService (sessions lost on restart)")
    session_service = InMemorySessionService()

runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await runner.close()

app = FastAPI(
    title="DietDoctorAI API",
    description="Production API for DietDoctorAI agent (ADK + FastAPI)",
    version="1.0.0",
    lifespan=lifespan,
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class InjectRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = "default_user"
    message: str
    role: Optional[str] = "model"

class InjectResponse(BaseModel):
    status: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    user_id = request.user_id or "default_user"
    session_id = request.session_id or str(uuid.uuid4())
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={"_session_id": session_id, "_user_id": user_id},
        )
    content = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )
    response_parts: list[str] = []
    try:
        async with Aclosing(
            runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            )
        ) as events:
            async for event in events:
                if getattr(event, "partial", False):
                    continue
                if not event.content or not event.content.parts:
                    continue
                if event.content.role == "user":
                    continue
                text = "".join(
                    part.text for part in event.content.parts if part.text
                )
                if text.strip():
                    response_parts.append(text.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    response_text = "\n\n".join(response_parts)
    return ChatResponse(
        response=response_text,
        session_id=session_id,
    )

@app.post("/inject", response_model=InjectResponse)
async def inject(request: InjectRequest) -> InjectResponse:
    user_id = request.user_id or "default_user"
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=request.session_id,
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        event = Event(
            invocation_id=str(uuid.uuid4()),
            author="root_agent" if request.role == "model" else "user",
            content=types.Content(
                role=request.role or "model",
                parts=[types.Part(text=request.message)],
            ),
        )
        await session_service.append_event(session=session, event=event)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return InjectResponse(status="ok", session_id=request.session_id)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
