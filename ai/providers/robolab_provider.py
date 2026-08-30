from __future__ import annotations
import os
import httpx
from ai.base import AIProvider

class RoboLabProvider(AIProvider):
    name = "robolab"

    def available(self) -> bool:
        return bool(os.getenv("ROBO_MODEL_URL"))

    def generate(self, system: str, prompt: str, model: str | None = None):
        url = os.getenv("ROBO_MODEL_URL", "").rstrip("/")
        key = os.getenv("ROBO_MODEL_API_KEY", "")
        model = model or os.getenv("AI_MODEL", "robolab-code")
        if not url:
            return {"status":"failed","error_code":"ROBO_MODEL_NOT_CONFIGURED","message":"ROBO_MODEL_URL is required.","recoverable":True}
        headers = {"content-type":"application/json"}
        if key:
            headers["authorization"] = f"Bearer {key}"
        try:
            with httpx.Client(timeout=180) as client:
                r = client.post(f"{url}/generate", headers=headers, json={"model":model,"system":system,"prompt":prompt})
                r.raise_for_status()
                raw = r.json()
                return {"status":"passed","data":raw.get("data",raw),"provider":self.name,"model":model}
        except Exception as exc:
            return {"status":"failed","error_code":"ROBO_MODEL_REQUEST_FAILED","message":str(exc),"recoverable":True}
