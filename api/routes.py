from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from .location import detect_country
from .pricing import plans_for_country
from .codegen import generate_code
from .project import analyze_idea
from services.engine import orchestrator
from ai.model_registry import public_registry

router=APIRouter()

class Idea(BaseModel): description: str = Field(min_length=1,max_length=20000)
class CodeRequest(BaseModel):
    description: str = Field(min_length=1,max_length=20000)
    board: str = "Arduino Uno"
    language: str = "Arduino C++"
class EngineRequest(BaseModel):
    description: str | None = Field(default=None,max_length=30000)
    idea: str | None = Field(default=None,max_length=30000)
    code: str | None = Field(default=None,max_length=100000)
    board: str = "Arduino Uno"
    language: str = "Arduino C++"
    project: dict = Field(default_factory=dict)

@router.get("/status")
async def status(): return {"status":"online","message":"RoboLab engineering platform is running.","version":"4.2.0"}
@router.get("/ai/providers")
async def providers(): return orchestrator.provider_status()
@router.get("/ai/models")
async def models(): return {"object":"list","data":public_registry()}
@router.get("/location")
async def location(request: Request): return await detect_country(request)
@router.get("/pricing")
async def pricing(request: Request):
    country=(await detect_country(request)).get("country","IN")
    return {"country":country,"plans":plans_for_country(country)}
@router.post("/idea/analyze")
async def idea_analyze(item: Idea): return analyze_idea(item.description)
@router.post("/code/generate")
async def code(item: CodeRequest): return generate_code(item.description,item.board,item.language)

VALID_STAGES={"architect","component","circuit","code","cad","simulation","verify","verifier_1","verifier_2","compile","compiler_1","compiler_2","audit","consensus","bom","debug","documentation"}

def _run(stage: str, data: EngineRequest):
    stage=stage.lower()
    if stage not in VALID_STAGES: raise HTTPException(status_code=404, detail=f"Unknown AI stage: {stage}")
    payload=data.model_dump()
    if stage in {"bom","debug"}:
        if stage=="bom": return {"stage":stage,"mode":"native-engine","result":orchestrator.run(stage,payload).get("result")}
        return {"stage":stage,"mode":"native-engine","result":orchestrator.run(stage,payload).get("result")}
    return orchestrator.run(stage,payload)

@router.post("/ai/{stage}")
async def ai_stage(stage: str, data: EngineRequest): return _run(stage,data)
