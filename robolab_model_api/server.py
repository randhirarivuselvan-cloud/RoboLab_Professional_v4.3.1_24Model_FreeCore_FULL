from __future__ import annotations

import os
import time
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from ai.local_models.registry import MODEL_SPECS, model_for, public_registry
from ai.local_models.runtime import LocalModelRuntime

APP_NAME = "RoboLab Local Model Gateway"
API_KEY = os.getenv("ROBO_MODEL_API_KEY", "")
DEFAULT_ROLE = os.getenv("ROBO_DEFAULT_ROLE", "code")
app = FastAPI(title=APP_NAME, version="3.0.0")
runtime = LocalModelRuntime()


def _auth(authorization: str | None = Header(default=None)) -> None:
    if not API_KEY:
        return
    if not authorization or not authorization.startswith("Bearer ") or authorization[7:].strip() != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")


def resolve_role(model: str | None, role: str | None) -> str:
    if role in MODEL_SPECS:
        return str(role)
    if model in MODEL_SPECS:
        return str(model)
    for candidate in MODEL_SPECS:
        if model_for(candidate) == model:
            return candidate
    return DEFAULT_ROLE


class GenerateRequest(BaseModel):
    model: str | None = None
    role: str | None = None
    system: str = "You are RoboLab's local engineering model."
    prompt: str = Field(min_length=1, max_length=100000)


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1, max_length=100000)


class ChatRequest(BaseModel):
    model: str | None = None
    role: str | None = None
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


def _infer(role: str, prompt: str) -> dict:
    result = runtime.generate(role, prompt)
    if result["state"] != "COMPLETED":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.get("/health")
def health(_: None = Depends(_auth)):
    states = [runtime.status(role) for role in MODEL_SPECS]
    ready = sum(state["state"] == "TRAINED_LOCAL" for state in states)
    return {
        "status": "ok",
        "service": APP_NAME,
        "models": len(MODEL_SPECS),
        "models_trained_local": ready,
        "network_used": False,
        "external_ai_providers_disabled": True,
    }


@app.get("/v1/models")
def models(_: None = Depends(_auth)):
    return {"object": "list", "data": public_registry()}


@app.post("/generate")
def generate(req: GenerateRequest, _: None = Depends(_auth)):
    role = resolve_role(req.model, req.role)
    result = _infer(role, f"{req.system}\n\n{req.prompt}")
    return {"status": "passed", "provider": "robolab-local", "model": result["model"], "role": role, "data": {"text": result["response"], "similarity": result["similarity"]}, "network_used": False}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest, _: None = Depends(_auth)):
    role = resolve_role(req.model, req.role)
    prompt = "\n".join(f"{message.role.upper()}: {message.content}" for message in req.messages)
    result = _infer(role, prompt)
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": result["model"],
        "choices": [{"index": 0, "message": {"role": "assistant", "content": result["response"]}, "finish_reason": "stop"}],
        "network_used": False,
    }
