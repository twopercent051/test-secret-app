from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class ClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_host = x_forwarded_for.split(",")[0].strip()
        else:
            client_host = request.client.host
        request.state.client_ip = client_host
        response = await call_next(request)
        return response

