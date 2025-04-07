from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    return request.state.client_ip
