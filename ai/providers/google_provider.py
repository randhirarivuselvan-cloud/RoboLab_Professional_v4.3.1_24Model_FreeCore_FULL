from __future__ import annotations
import json, os
import httpx
from ai.base import AIProvider

class GoogleProvider(AIProvider):
    name = "google"
    def available(self) -> bool: return bool(os.getenv("AI_API_KEY"))
    def generate(self, system: str, prompt: str, model: str | None = None):
        key=os.getenv("AI_API_KEY",""); model=model or os.getenv("AI_MODEL","")
        if not key or not model: return {"status":"failed","error_code":"AI_NOT_CONFIGURED","message":"AI_API_KEY and AI_MODEL are required.","recoverable":True}
        try:
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            with httpx.Client(timeout=90) as client:
                r=client.post(url,json={"systemInstruction":{"parts":[{"text":system}]},"contents":[{"role":"user","parts":[{"text":prompt}]}]})
                r.raise_for_status(); candidates=r.json().get("candidates",[]); text=""
                if candidates: text="".join(p.get("text","") for p in candidates[0].get("content",{}).get("parts",[]))
                try: data=json.loads(text)
                except Exception: data={"text":text}
                return {"status":"passed","data":data,"provider":self.name,"model":model}
        except Exception as e: return {"status":"failed","error_code":"AI_REQUEST_FAILED","message":str(e),"recoverable":True}
