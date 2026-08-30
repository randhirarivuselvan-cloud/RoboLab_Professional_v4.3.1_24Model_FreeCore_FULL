from __future__ import annotations
import json, os
import httpx
from ai.base import AIProvider

class LocalProvider(AIProvider):
    name = "local"
    def available(self) -> bool: return bool(os.getenv("LOCAL_AI_URL"))
    def generate(self, system: str, prompt: str, model: str | None = None):
        url=os.getenv("LOCAL_AI_URL",""); model=model or os.getenv("AI_MODEL","") or "local"
        if not url: return {"status":"failed","error_code":"LOCAL_AI_NOT_CONFIGURED","message":"LOCAL_AI_URL is required.","recoverable":True}
        try:
            with httpx.Client(timeout=120) as client:
                r=client.post(url,json={"model":model,"system":system,"prompt":prompt})
                r.raise_for_status(); raw=r.json(); data=raw.get("data",raw)
                return {"status":"passed","data":data,"provider":self.name,"model":model}
        except Exception as e: return {"status":"failed","error_code":"AI_REQUEST_FAILED","message":str(e),"recoverable":True}
