import asyncio


class StreamablePromise:
    def __init__(self):
        self.chunks = asyncio.Queue()
        self._complete = asyncio.Event()

    async def append(self, chunk):
        await self.chunks.put(chunk)

    def done(self):
        self._complete.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._complete.is_set() and self.chunks.empty():
            raise StopAsyncIteration
        chunk = await self.chunks.get()
        if chunk is None:  # Signal for completion
            raise StopAsyncIteration
        return chunk

    async def get_full_response(self):
        result = []
        async for chunk in self:
            result.append(chunk)
        return "".join(result)
