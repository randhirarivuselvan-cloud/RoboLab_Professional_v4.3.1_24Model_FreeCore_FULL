"""Local-only provider selection. Vendor aliases cannot send any external request."""
from ai.providers.local_provider import LocalProvider
from ai.providers.none import NoneProvider

PROVIDERS = {"none": NoneProvider, "local": LocalProvider, "robolab": LocalProvider}

def build_provider(name: str | None):
    return PROVIDERS.get((name or "local").lower(), NoneProvider)()
