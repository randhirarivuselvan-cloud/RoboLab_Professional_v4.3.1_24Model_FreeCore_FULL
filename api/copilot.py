from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ai.assistant import copilot

router = APIRouter(prefix='/copilot', tags=['copilot'])

class CopilotRequest(BaseModel):
    message: str = Field(min_length=1, max_length=30000)
    action: str = Field(default='chat', max_length=80)
    context: dict[str, Any] = Field(default_factory=dict)

@router.get('/status')
async def status():
    return copilot.status()

@router.post('/chat')
async def chat(req: CopilotRequest):
    return copilot.chat(req.message, req.context, req.action)
