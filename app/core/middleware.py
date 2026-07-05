import asyncio
import json
import logging
import secrets
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.clients.observability_factory import observability

logger = logging.getLogger(__name__)

DATASET_NAME = "adversarial-tests"


async def _get_request_body(request: Request) -> bytes:
    """Safely get request body, handling already-read cases."""
    try:
        body = await request.body()
        return body
    except Exception:
        return b""


def handle_validation_error(
    request: Request,
    exc: RequestValidationError | ValidationError,
) -> JSONResponse:
    """Handle validation errors and capture them for adversarial test generation."""
    # Use asyncio.run for synchronous context or await if async
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in async context, but this function is called
            # synchronously from exception handler
            # So we need to use the body that was already read
            raw_payload = getattr(request, '_body', b'').decode(
                "utf-8", errors="replace"
            )
        else:
            body = loop.run_until_complete(_get_request_body(request))
            raw_payload = body.decode("utf-8", errors="replace")
    except Exception:
        raw_payload = ""

    errors = exc.errors() if hasattr(exc, "errors") else []

    def _json_safe(value):
        if isinstance(value, dict):
            return {k: _json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_json_safe(v) for v in value]
        if hasattr(value, "isoformat"):
            return value.isoformat()
        try:
            json.dumps(value)
            return value
        except TypeError:
            return str(value)

    safe_errors = _json_safe(errors)

    # Create trace for observability
    trace = observability.trace(
        name="validation_error",
        metadata={
            "endpoint": str(request.url.path),
            "method": request.method,
            "error_type": "pydantic_validation",
            "errors": safe_errors,
        },
        input=raw_payload,
    )

    # Add to dataset for adversarial test generation
    try:
        observability.create_dataset(
            name=DATASET_NAME,
            description="Captured validation errors for adversarial test generation",
            metadata={"source": "exception_handler", "auto_created": True},
        )
    except Exception:
        pass  # Dataset may already exist

    # Create dataset item from the trace
    try:
        observability.create_dataset_item(
            dataset_name=DATASET_NAME,
                input={
                    "payload": raw_payload,
                    "endpoint": str(request.url.path),
                    "method": request.method,
                },
                expected_output={
                    "error_type": "pydantic_validation",
                    "errors": safe_errors,
                    "hint": "This payload should be handled gracefully or rejected with a clear error",
                },
                source_trace_id=trace.id if hasattr(trace, "id") else str(id(trace)),
                metadata={
                    "error_count": len(errors),
                },
            )
    except Exception as dataset_exc:
        logger.warning(
            "failed_to_create_dataset_item: %s", str(dataset_exc)
        )

    trace_id = trace.id if hasattr(trace, "id") else str(id(trace))
    logger.warning(
        "validation_error_captured endpoint=%s errors=%s trace_id=%s dataset=%s",
        request.url.path,
        errors,
        trace_id,
        DATASET_NAME,
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": safe_errors,
            "hint": "This payload has been captured for adversarial test generation.",
            "trace_id": trace_id,
        },
    )


class AdversarialTestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Any:
        try:
            return await call_next(request)
        except (RequestValidationError, ValidationError) as exc:
            return handle_validation_error(request, exc)


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        cookie_name: str = "csrf_token",
        header_name: str = "x-csrf-token",
    ) -> None:
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Any:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            response = await call_next(request)
            token = request.cookies.get(self.cookie_name)
            if not token:
                token = secrets.token_urlsafe(32)
                response.set_cookie(
                    self.cookie_name,
                    token,
                    httponly=True,
                    samesite="lax",
                    secure=request.url.scheme == "https",
                )
            return response

        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                header_token = request.headers.get(self.header_name)
                cookie_token = request.cookies.get(self.cookie_name)
                if not header_token or not cookie_token or header_token != cookie_token:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF token missing or invalid."},
                    )
                return await call_next(request)

            form_data = await request.form()
            form_token = form_data.get("csrf_token")
            cookie_token = request.cookies.get(self.cookie_name)
            if not form_token or not cookie_token or form_token != cookie_token:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token missing or invalid."},
                )

        return await call_next(request)


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(AdversarialTestMiddleware)
    # app.add_middleware(CSRFMiddleware) MVP

    # Also register as exception handler to catch errors before default handler
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return handle_validation_error(request, exc)

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return handle_validation_error(request, exc)
