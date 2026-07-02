class TracePilotException(Exception):
    status_code = 500
    detail = "Internal server error"


class LLMError(TracePilotException):
    status_code = 502
    detail = "LLM provider error"


class LangfuseError(TracePilotException):
    status_code = 502
    detail = "Observability error"
