from __future__ import annotations
import json, os
from typing import Any
import httpx
from ai.base import AIProvider

class OpenAIProvider(AIProvider):
    name = "openai"
    def available(self) -> bool:
        return bool(os.getenv("AI_API_KEY"))
    def generate(self, system: str, prompt: str, model: str | None = None) -> dict[str, Any]:
        key = os.getenv("AI_API_KEY", "")
        model = model or os.getenv("AI_MODEL", "")
        base = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if not key or not model:
            return {"status": "failed", "error_code": "AI_NOT_CONFIGURED", "message": "AI_API_KEY and AI_MODEL are required.", "recoverable": True}
        try:
            with httpx.Client(timeout=90) as client:
                r = client.post(f"{base}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json={"model": model, "messages": [{"role":"system","content":system},{"role":"user","content":prompt}], "temperature": 0.15})
                r.raise_for_status()
                data = r.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                try: parsed = json.loads(text)
                except Exception: parsed = {"text": text}
                return {"status":"passed","data":parsed,"provider":self.name,"model":model}
        except Exception as e:
            return {"status":"failed","error_code":"AI_REQUEST_FAILED","message":str(e),"recoverable":True}
