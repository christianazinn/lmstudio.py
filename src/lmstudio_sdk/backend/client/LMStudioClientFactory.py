from .AsyncLMStudioClient import AsyncLMStudioClient
from .SyncLMStudioClient import SyncLMStudioClient


# pseudo-constructor haha - also awaitable!
def LMStudioClient(
    base_url: str | None = None,
    client_identifier: str | None = None,
    client_passkey: str | None = None,
    is_async: bool = False,
) -> AsyncLMStudioClient | SyncLMStudioClient:
    """
    Constructs an instance of either `AsyncLMStudioClient` or `SyncLMStudioClient` based on the value of `is_async`.
    Default: `False`. If `True`, this will need to be `await`ed.
    """
    client = (
        AsyncLMStudioClient(base_url, client_identifier, client_passkey)
        if is_async
        else SyncLMStudioClient(base_url, client_identifier, client_passkey)
    )
    return client.connect() if is_async else client
