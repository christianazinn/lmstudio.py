import inspect
from typing import Any, Coroutine, Optional

from .AsyncLMStudioClient import AsyncLMStudioClient
from .SyncLMStudioClient import SyncLMStudioClient


# TODO: would be nice to use a context manager so close() is handled automatically
def LMStudioClient(
    base_url: Optional[str] = None,
    client_identifier: Optional[str] = None,
    client_passkey: Optional[str] = None,
) -> SyncLMStudioClient | Coroutine[Any, Any, AsyncLMStudioClient]:
    """Constructs an LM Studio client connected to the server.

    Args:
    - base_url: The URL of the LM Studio server.
    - client_identifier: The unique identifier for the client.
    - client_passkey: The passkey for the client.

    If these are not provided, the client will attempt to guess the base URL,
    and generate random values for the client identifier and passkey.

    Returns:
    - An instance of `AsyncLMStudioClient` or `SyncLMStudioClient`
      connected to the server. `awaiting` this function will return the former.

    Raises:
    - ValueError: If a connection cannot be established.
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
