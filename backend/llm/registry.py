from backend.llm.base import BaseLLMProvider

PROVIDERS: dict[str, type[BaseLLMProvider]] = {}


def _register_defaults():
    from backend.llm.openai_provider import OpenAIProvider
    PROVIDERS["openai"] = OpenAIProvider


def get_provider(name: str | None = None) -> BaseLLMProvider:
    if not PROVIDERS:
        _register_defaults()

    if name is None:
        from backend.config import get_config
        name = get_config().llm_provider

    if name not in PROVIDERS:
        raise ValueError(f"Unknown LLM provider '{name}'. Available: {list(PROVIDERS.keys())}")

    return PROVIDERS[name]()
