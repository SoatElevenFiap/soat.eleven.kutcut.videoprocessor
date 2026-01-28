import uuid
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

http_correlation_id_var: ContextVar[str] = ContextVar[str]("http_correlation_id", default="")

class HttpCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        http_correlation_id = str(uuid.uuid4())[:8]
        http_correlation_id_var.set(http_correlation_id)
        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = http_correlation_id
        return response

def get_http_correlation_id() -> str:
    return http_correlation_id_var.get()
