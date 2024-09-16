import asyncio
from WebSocketBackendClient import WebSocketBackendClient


class LMStudioClient:
    master_channel_id = 0

    # TODO other init options
    def __init__(self, websocket_uri: str):
        self.client = WebSocketBackendClient(websocket_uri)

    async def connect(self):
        await self.client.connect()

    async def close(self):
        await self.client.close()

    # TODO implement all endpoints
    # TODO cf. ts sdk for signatures

    async def load_model(self, model_path: str):
        loading_complete = asyncio.Event()
        result = {}

        async def handle_model_loading(message):
            if message["type"] == "progress":
                print(f"Loading progress: {message['progress'] * 100:.2f}%")
            elif message["type"] == "success":
                result.update(message)
                loading_complete.set()

        # TODO: typing ugh
        payload = {
            "path": model_path,
            "loadConfigStack": {"layers": []},
            "noHup": False,
        }

        await self.client.init_channel("loadModel", payload, handle_model_loading)

        await loading_complete.wait()
        return result

    async def unload_model(self, model_path: str):
        await self.client.rpc_call("unloadModel", {"identifier": model_path})
