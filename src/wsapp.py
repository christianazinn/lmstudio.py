from websocket import WebSocketApp, WebSocket
from typing import Any
from asyncio import sleep
import json
import threading


class AuthenticatedClient:

    app: WebSocketApp
    authenticated: bool = False
    daemon: threading.Thread | None = None
    receivedData: list[str] = []
    sendDataQueue: list[str] = []  # TODO do something with me

    def __init__(self, url: str | None, **kwargs: Any):
        if url is None:
            raise ValueError("url must be provided")
            # TODO infer
        self.app = WebSocketApp(url, on_open=self.open_callback(),
                                on_error=self.error_callback(),
                                on_data=self.data_callback(),
                                **kwargs)

    async def authenticate(self, poll_rate: int = 2, timeout: int = 120) -> bool:
        try:
            # return if already authenticated
            if self.authenticated:
                return True

            # start the websocket thread
            self.daemon = threading.Thread(target=self.app.run_forever)
            self.daemon.daemon = True
            self.daemon.start()

            while len(self.receivedData) == 0:
                if timeout <= 0:
                    self.authenticated = False
                    return False
                timeout -= poll_rate
                await sleep(poll_rate)

            if "success" in self.receivedData[0] and self.receivedData[0]["success"] == True:
                self.authenticated = True
                self.receivedData.pop(0)
            return self.authenticated
        except Exception as e:
            print(e)  # TODO better error handling
            return self.authenticated

    def open_callback(self) -> Any:
        def on_open(ws: WebSocket):
            print("Connected")
            # authentication
            ws.send(json.dumps({
                "authVersion": 1,
                "clientIdentifier": "pytest",
                "clientPasskey": "pytest"
            }))
        return on_open

    def error_callback(self) -> Any:
        def on_error(ws: WebSocket, error: Any):
            print("Error: ", error)
        return on_error

    def data_callback(self) -> Any:
        def on_data(ws: WebSocket, data: str, a: Any, b: Any):
            self.receivedData.append(data)
            print(data)
            # print(len(self.receivedData))
        return on_data
