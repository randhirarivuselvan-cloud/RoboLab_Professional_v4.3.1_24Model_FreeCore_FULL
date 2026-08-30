from __future__ import annotations
import json, os
import httpx
from ai.base import AIProvider

class AnthropicProvider(AIProvider):
    name = "anthropic"
    def available(self) -> bool: return bool(os.getenv("AI_API_KEY"))
    def generate(self, system: str, prompt: str, model: str | None = None):
        key = os.getenv("AI_API_KEY", ""); model = model or os.getenv("AI_MODEL", "")
        if not key or not model: return {"status":"failed","error_code":"AI_NOT_CONFIGURED","message":"AI_API_KEY and AI_MODEL are required.","recoverable":True}
        try:
            with httpx.Client(timeout=90) as client:
                r = client.post("https://api.anthropic.com/v1/messages", headers={"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"}, json={"model":model,"max_tokens":8000,"system":system,"messages":[{"role":"user","content":prompt}]})
                r.raise_for_status(); text="".join(x.get("text","") for x in r.json().get("content",[]))
                try: data=json.loads(text)
                except Exception: data={"text":text}
                return {"status":"passed","data":data,"provider":self.name,"model":model}
        except Exception as e: return {"status":"failed","error_code":"AI_REQUEST_FAILED","message":str(e),"recoverable":True}
