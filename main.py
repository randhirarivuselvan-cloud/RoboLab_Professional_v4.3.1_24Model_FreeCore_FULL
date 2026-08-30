from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.copilot import router as copilot_router

VERSION="4.2.0"
BASE=Path(__file__).resolve().parent
STATIC=BASE/"web"/"static"
app=FastAPI(title="RoboLab",version=VERSION)
origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins else ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router,prefix="/api")
app.include_router(copilot_router,prefix="/api")
app.mount("/static",StaticFiles(directory=str(STATIC)),name="static")

@app.get("/")
async def home(): return FileResponse(str(STATIC/"index.html"))
@app.get("/health")
async def health(): return {"status":"online","app":"RoboLab","version":VERSION}
