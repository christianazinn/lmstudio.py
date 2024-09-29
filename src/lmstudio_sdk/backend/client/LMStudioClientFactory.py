import inspect
from typing import Any, Coroutine, Optional

from .AsyncLMStudioClient import AsyncLMStudioClient
from .SyncLMStudioClient import SyncLMStudioClient


def LMStudioClient(
    base_url: Optional[str] = None,
    client_identifier: Optional[str] = None,
    client_passkey: Optional[str] = None,
) -> SyncLMStudioClient | Coroutine[Any, Any, AsyncLMStudioClient]:
    """Constructs an instance of either `AsyncLMStudioClient` or `SyncLMStudioClient`.

    Just `await` for async!
    """
    is_async = (
        inspect.currentframe().f_back.f_code.co_flags & inspect.CO_COROUTINE
    )
    client = (
        AsyncLMStudioClient(base_url, client_identifier, client_passkey)
        if is_async
        else SyncLMStudioClient(base_url, client_identifier, client_passkey)
    )
    return client.connect()
