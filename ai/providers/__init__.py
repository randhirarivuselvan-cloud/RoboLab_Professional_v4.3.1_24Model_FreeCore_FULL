from ai.providers.none import NoneProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.anthropic_provider import AnthropicProvider
from ai.providers.google_provider import GoogleProvider
from ai.providers.local_provider import LocalProvider
from ai.providers.robolab_provider import RoboLabProvider

PROVIDERS = {
    "none": NoneProvider,
    "openai": OpenAIProvider,
    "openai_compatible": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "gemini": GoogleProvider,
    "local": LocalProvider,
    "robolab": RoboLabProvider,
    "custom": RoboLabProvider,
}

def build_provider(name: str | None):
    return PROVIDERS.get((name or "none").lower(), NoneProvider)()
