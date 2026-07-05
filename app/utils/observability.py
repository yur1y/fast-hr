from app.config import settings


def get_trace_url(trace_id: str) -> str | None:
    provider = settings.observability_provider.lower()

    if provider == "langfuse":
        base = settings.langfuse_base_url or settings.langfuse_host
        if settings.langfuse_project_id:
            return f"{base}/project/{settings.langfuse_project_id}/traces?search={trace_id}&searchType=id&searchType=content"
        return f"{base}/trace/{trace_id}"

    if provider == "langsmith":
        return f"{settings.langsmith_host}/traces/{trace_id}"

    if provider == "phoenix":
        return f"{settings.phoenix_host}/projects/{settings.phoenix_project_name}/traces/{trace_id}"

    return None
