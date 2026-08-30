import os
import httpx
from fastapi import Request

async def detect_country(request: Request):
    # Render/proxy-aware client IP detection. Local/private addresses fall back to IN.
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not ip:
        ip = request.client.host if request.client else ""
    if ip in {"127.0.0.1", "::1", "localhost"} or ip.startswith(("10.", "192.168.", "172.")):
        return {"country": os.getenv("DEFAULT_COUNTRY", "IN"), "source": "local-default"}
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(f"https://ipapi.co/{ip}/json/")
            data = r.json()
            code = data.get("country_code")
            if code:
                return {"country": code.upper(), "source": "ip"}
    except Exception:
        pass
    return {"country": os.getenv("DEFAULT_COUNTRY", "IN"), "source": "fallback"}
