# pylance: disable=unused-imports
# flake8: noqa: f401
# ruff: noqa: F401
"""Utility functions/classes and ported TypeScript classes.

Classes:
    AsyncAbortSignal: An asynchronous signal that can be used to abort an operation.
    SyncAbortSignal:A synchronous signal that can be used to abort an operation.
    ChannelError: An error that occurs during a channel operation.
    RPCError: An error that occurs during an RPC call.

Logging:
    get_logger: A function to get a logger for the SDK.
    RECV: Debug level for sent and received packets from the LM Studio server.
    SEND: Debug level for sent packets to the LM Studio server
    WEBSOCKET: Debug level for WebSocket connection events.
"""

from .AbortSignal import AsyncAbortSignal, SyncAbortSignal
from .BufferedEvent import (
    AsyncBufferedEvent,
    SyncBufferedEvent,
)
from .logger import get_logger, RECV, SEND, WEBSOCKET
from .PseudoFuture import PseudoFuture
from .utils import (
    _assert,
    ChannelError,
    generate_random_base64,
    lms_default_ports,
    LiteralOrCoroutine,
    number_to_checkbox_numeric,
    pretty_print,
    pretty_print_error,
    RPCError,
)

__all__ = [
    "AsyncAbortSignal",
    "ChannelError",
    "get_logger",
    "RECV",
    "RPCError",
    "SEND",
    "SyncAbortSignal",
    "WEBSOCKET",
]
