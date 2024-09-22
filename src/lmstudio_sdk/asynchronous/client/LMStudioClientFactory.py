from .AsyncLMStudioClient import AsyncLMStudioClient
from .SyncLMStudioClient import SyncLMStudioClient
from ...common import LMStudioClientConstructorOpts


class LMStudioClientFactory:
    # python does not have async constructors so we do this
    # TODO: unpack LMStudioClientConstructorOpts
    @staticmethod
    def create(is_async: bool = False, opts: LMStudioClientConstructorOpts | None = None):
        client = AsyncLMStudioClient(opts) if is_async else SyncLMStudioClient(opts)
        return client.connect() if is_async else client
