import asyncio

from AsyncIterable import StreamablePromise
from TypesAndInterfaces.relevant.Defaults.ClientPort import ClientPort
from TypesAndInterfaces.relevant.LLMGeneralSettings.KVConfig import KVConfig

from TypesAndInterfaces.relevant.Namespaces.SystemNamespace import SystemNamespace


class LMStudioClient:
    master_channel_id = 0

    # TODO other init options
    def __init__(self, websocket_uri: str):
        self.client = ClientPort(websocket_uri)

    async def connect(self):
        await self.client.connect()

    async def close(self):
        await self.client.close()

    # TODO implement all endpoints
    # TODO cf. ts sdk for signatures

    async def load_model(self, model_path: str):
        loading_complete = asyncio.Event()
        result = {}

        async def handle_communications(message):
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

        await self.client.create_channel("loadModel", payload, handle_communications)

        await loading_complete.wait()
        return result

    def predict(self, model_path: str) -> StreamablePromise:
        completion_stream = StreamablePromise()

        async def handle_communications(message):
            if message["type"] == "fragment":
                await completion_stream.append(message["fragment"])
            elif message["type"] == "success":
                await completion_stream.append(None)  # Signal completion
                completion_stream.done()

        async def run_prediction():
            payload = {
                "modelSpecifier": {"type": "query", "query": {"identifier": model_path}},
                "context": {
                    "history": [{"role": "user", "content": [{"type": "text", "text": "Hello, how are you?"}]}]
                },
                "config": {},
                "predictionConfigStack": {"layers": []},
            }
            await self.client.create_channel("predict", payload, handle_communications)

        # Start the chat completion process without awaiting it
        asyncio.create_task(run_prediction())

        return completion_stream

    async def getLoadConfig(self, identifier: str):
        model_specifier = {
            "type": "query",
            "query": {
                "identifier": identifier,
            },
        }

        result = await self.client.call_rpc("getLoadConfig", {"specifier": model_specifier})
        return KVConfig.model_validate(result)
    
    async def list_downloaded_models(self):
        systemNamespace = SystemNamespace()
        systemNamespace.port = self.client
        return await systemNamespace.list_downloaded_models()

    async def unload_model(self, model_path: str):
        await self.client.call_rpc("unloadModel", {"identifier": model_path})
