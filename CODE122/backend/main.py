from fastapi import FastAPI
from pydantic import BaseModel
from CODE122.core.schema import EngineeringProject
from CODE122.core.pipeline import run_engineering_pipeline
from CODE122.core.ai_registry import status

app = FastAPI(title="RoboLab CODE122", version="0.1.0")

class ProjectPayload(BaseModel):
    project: dict

@app.get("/api/v1/health")
def health():
    return {"service":"RoboLab","code":"CODE122","status":"ONLINE"}

@app.get("/api/v1/models")
def models():
    return {"count": 48, "models": status()}

@app.post("/api/v1/engineering/validate")
def validate(payload: ProjectPayload):
    project = EngineeringProject.from_dict(payload.project)
    return run_engineering_pipeline(project)
