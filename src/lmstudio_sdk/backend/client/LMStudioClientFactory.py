import inspect
from .AsyncLMStudioClient import AsyncLMStudioClient
from .SyncLMStudioClient import SyncLMStudioClient


# pseudo-constructor haha - also awaitable!
def LMStudioClient(
    base_url: str | None = None,
    client_identifier: str | None = None,
    client_passkey: str | None = None,
) -> AsyncLMStudioClient | SyncLMStudioClient:
    """
    Constructs an instance of either `AsyncLMStudioClient` or `SyncLMStudioClient`. Just `await` for async!
    """
    is_async = inspect.currentframe().f_back.f_code.co_flags & inspect.CO_COROUTINE
    client = (
        AsyncLMStudioClient(base_url, client_identifier, client_passkey)
        if is_async
        else SyncLMStudioClient(base_url, client_identifier, client_passkey)
    )
    return client.connect() if is_async else client
