import asyncio
import json
import websockets
from typing import Any, Callable, Optional

import lmstudio_sdk.utils as utils

from .BaseClientPort import BaseClientPort


logger = utils.get_logger(__name__)


class AsyncClientPort(BaseClientPort):
    def __init__(self, uri: str, endpoint: str, identifier: str, passkey: str):
        super().__init__(uri, endpoint, identifier, passkey)
        self.running = False
        self.receive_task = None

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

                data_type = data.get("type", None)
                if data_type is None:
                    continue

                # channel endpoints
                if data_type == "channelSend":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        message_content = data.get("message", data)
                        if message_content.get("type", None) == "log":
                            message_content = message_content.get("log")
                        self.channel_handlers[channel_id](message_content)
                elif data_type == "channelClose":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        del self.channel_handlers[channel_id]
                elif data_type == "channelError":
                    channel_id = data.get("channelId")
                    if channel_id in self.channel_handlers:
                        self.channel_handlers[channel_id](data)
                        del self.channel_handlers[channel_id]

                # RPC endpoints
                elif data_type == "rpcResult" or data_type == "rpcError":
                    call_id = data.get("callId", -1)
                    if call_id in self.rpc_handlers:
                        self.rpc_handlers[call_id](data)
                        del self.rpc_handlers[call_id]
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

    def _rpc_complete_event(self):
        return asyncio.Event()

    def _promise_event(self):
        return asyncio.Future()

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
