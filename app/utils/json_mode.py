SUPPORTS_JSON_MODEL = {
    "openai",
    "openai_compatible",
}


def supports_json_mode(provider: str) -> bool:
    return provider in SUPPORTS_JSON_MODEL
