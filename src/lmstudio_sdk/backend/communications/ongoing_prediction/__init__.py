# pylance: disable=unused-imports
# flake8: noqa: f401
# ruff: noqa: F401
"""Classes representing ongoing prediction processes.

Classes:
    AsyncOngoingPrediction: ongoing prediction using asyncio.
    SyncOngoingPrediction: ongoing prediction using blocking calls.

Each class is meant to mirror the TypeScript SDK as closely as possible.
Both are iterables: AsyncOngoingPrediction with `async for`, and
SyncOngoingPrediction with `for`. They yield fragments of the prediction
as they become available.

Alternatively, `result()` can be called to get the entire prediction
as a single string.
"""

from .AsyncOngoingPrediction import AsyncOngoingPrediction
from .BaseOngoingPrediction import BaseOngoingPrediction
from .SyncOngoingPrediction import SyncOngoingPrediction

__all__ = [
    "AsyncOngoingPrediction",
    "SyncOngoingPrediction",
]
