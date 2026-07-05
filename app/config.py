from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="TP_",
    )

    app_name: str = "TracePilot"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "info"

    api_v1_str: str = "/api/v1"

    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"

    # LLM provider
    llm_provider: str = "openai"
    openai_api_key: str = "ollama"
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    grok_api_key: str | None = None
    grok_base_url: str | None = None
    grok_model: str = "grok-beta"
    grok_temperature: float = 0.7
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 0.7
    google_api_key: str | None = None
    google_model: str = "gemini-2.0-flash"
    google_temperature: float = 0.7

    # Ollama-specific settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_num_ctx: int = 2048
    ollama_num_gpu: int = 1
    ollama_keep_alive: str = "5m"

    # Observability provider
    observability_provider: str = "langfuse"
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_base_url: str | None = None
    langfuse_project_id: str | None = None
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

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True

    cleanup_retention_days: int = 90
    cleanup_batch_size: int = 500


settings = Settings()
