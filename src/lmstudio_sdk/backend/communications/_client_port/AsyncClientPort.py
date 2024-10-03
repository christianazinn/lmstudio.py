import asyncio
import json
import websockets
from typing import Any, Callable, Optional
from typing_extensions import override

import lmstudio_sdk.utils as utils

from .BaseClientPort import BaseClientPort


logger = utils.get_logger(__name__)


class AsyncClientPort(BaseClientPort):
    """Asynchronous client port for LM Studio communication.

    See `BaseClientPort` for more information.
    """

    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self.running = False
        self.receive_task = None

    @override
    async def connect(self):
        logger.websocket("Connecting to WebSocket at %s...", self.uri)
        self._websocket = await websockets.connect(self.uri)
        logger.websocket(
            "Connected to WebSocket at %s. \
            Sending authentication packet as %s...",
            self.uri,
            self.identifier,
        )
        await self._websocket.send(
            json.dumps(
                {
                    "authVersion": self._auth_version,
                    "clientIdentifier": self.identifier,
                    "clientPasskey": self._passkey,
                }
            )
        )
        self.running = True
        logger.websocket(
            "Async port authenticated: %s. Establishing receive task.",
            self.endpoint,
        )
        self.receive_task = asyncio.create_task(self.__receive_messages())

    @override
    async def close(self):
        self.running = False
        if self._websocket:
            logger.websocket(
                "Closing WebSocket connection on async port %s...",
                self.endpoint,
            )
            await self._websocket.close()
            logger.websocket(
                "WebSocket connection closed to %s.", self.endpoint
            )
        if self.receive_task:
            try:
                logger.websocket(
                    "Waiting for receive task to time out on async port %s...",
                    self.endpoint,
                )
                await asyncio.wait_for(self.receive_task, timeout=5.0)
                logger.websocket(
                    "Receive task timed out on async port %s.", self.endpoint
                )
            except asyncio.TimeoutError:
                logger.error(
                    "Receive task did not complete in time on async port %s!",
                    self.endpoint,
                )

    async def __receive_messages(self):
        """Receive messages from the WebSocket connection.

        This method is a coroutine that runs indefinitely, waiting for messages
        from the WebSocket connection. When a message is received, it is logged
        and passed to the `_handle_data` method for processing, after which
        the method waits for the next message.
        """
        try:
            while self.running:
                assert self._websocket is not None
                logger.recv(
                    "Waiting for message on async port %s.", self.endpoint
                )
                message = await self._websocket.recv()

                data = json.loads(message)
                logger.recv(
                    "Message received on async port %s:\n%s",
                    self.endpoint,
                    utils.pretty_print(data),
                )
                self._handle_data(data)
        except AssertionError:
            logger.error(
                "WebSocket connection not established in \
                receive_messages to %s: this should never happen?",
                self.uri,
            )
        except websockets.ConnectionClosedOK:
            logger.websocket(
                "WebSocket connection to closed normally to %s.", self.uri
            )
        except websockets.ConnectionClosedError as e:
            logger.error("WebSocket connection closed with error: %s", str(e))
        finally:
            self.running = False

    @override
    async def _send_payload(
        self,
        payload: dict,
        extra: Optional[dict] = None,
        postprocess: Optional[Callable[[dict], Any]] = None,
    ):
        if not self._websocket:
            logger.error(
                "Attempted to send payload, \
                but WebSocket connection is not established to %s.",
                self.uri,
            )
            raise ValueError("WebSocket connection not established.")
        logger.send(
            "Sending payload on async port %s:\n%s",
            self.endpoint,
            utils.pretty_print(payload),
        )
        await self._websocket.send(json.dumps(payload))
        if postprocess:
            return postprocess(extra)
        return extra

    @override
    def _rpc_complete_event(self):
        return asyncio.Event()

    @override
    def _promise_event(self):
        return asyncio.Future()

    @override
    async def _call_rpc(
        self,
        payload: dict,
        complete: asyncio.Event,
        result: dict,
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ):
        await self._send_payload(payload)
        logger.debug(
            "Waiting for RPC call to complete to %s...",
            payload.get("endpoint", "unknown"),
        )
        # TODO that's not very asynchronous of you:
        # this blocks anyway! should return a Future or similar
        await complete.wait()

        if "error" in result:
            logger.error(
                "Error in RPC call: %s",
                utils.pretty_print_error(result.get("error")),
            )
            raise utils.RPCError(
                "Error in RPC call: %s",
                result.get("error").get("title", "Unknown error"),
            )

        result = result.get("result", result)
        if isinstance(result, dict):
            result.update({"extra": extra})
        else:
            result = {"result": result, "extra": extra}

        def process_result(x):
            if isinstance(x, dict):
                return x.get("result", x)
            return x

        return process_result(postprocess(result))
