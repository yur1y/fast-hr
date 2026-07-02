from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TracePilot"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "info"

    api_v1_str: str = "/api/v1"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # LLM provider
    llm_provider: str = "openai"
    openai_api_key: str = "ollama"
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 0.7
    google_api_key: str | None = None
    google_model: str = "gemini-2.0-flash"
    google_temperature: float = 0.7

    # Observability provider
    observability_provider: str = "langfuse"
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_flush_at: int = 15
    langfuse_flush_interval: int = 1
    langsmith_api_key: str | None = None
    langsmith_host: str = "https://api.smith.langchain.com"
    phoenix_api_key: str | None = None
    phoenix_host: str = "https://app.phoenix.arize.com"
    phoenix_project_name: str = "tracepilot"

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    github_token: str | None = None
    github_repo: str | None = None

    fuzzer_default_count: int = 10
    fuzzer_detection_threshold: float = 0.7

    canary_threshold: float = 0.15
    canary_candidates_dir: str = "canary/candidates"


settings = Settings()
