import json
import asyncio
from wsapp import AuthenticatedClient
from time import sleep


async def main():
    
    print("Connecting to the server...")

    wsapp = AuthenticatedClient(url="ws://localhost:1234/llm")
    print(await wsapp.authenticate())

    sleep(5)
    print("hjio")
    wsapp.app.send(json.dumps({
        "type": "channelCreate",
        "endpoint": "loadModel",
        "channelId": 0,
        "creationParameter": {
            "path": "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf",
            "loadConfigStack": {"layers": []},
            "noHup": False
        }
    }))
    sleep(5)

    wsapp.app.close()

    print("Connection closed")

asyncio.get_event_loop().run_until_complete(main())
# on completion: "message": {"type": "success"}
# and "type": "channelClose"