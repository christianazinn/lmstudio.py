import logging


WRAPPER = 5
"""
Debug level for tracing calls, parameters, and return values for async/sync decorated wrapped functions.
The most verbose debug level offered - will log everything.
"""

RECV = 7
"""Debug level for sent and received packets from the LM Studio server."""

SEND = 8
"""Debug level for sent packets to the LM Studio server"""

WEBSOCKET = 9
"""Debug level for WebSocket connection events."""

logging.addLevelName(WRAPPER, "WRAPPER")
logging.addLevelName(RECV, "RECV")
logging.addLevelName(SEND, "SEND")
logging.addLevelName(WEBSOCKET, "WEBSOCKET")


def wrapper(self, message, *args, **kws):
    if self.isEnabledFor(WRAPPER):
        self._log(WRAPPER, message, args, **kws)


def recv(self, message, *args, **kws):
    if self.isEnabledFor(RECV):
        self._log(RECV, message, args, **kws)


def send(self, message, *args, **kws):
    if self.isEnabledFor(SEND):
        self._log(SEND, message, args, **kws)


def websocket(self, message, *args, **kws):
    if self.isEnabledFor(WEBSOCKET):
        self._log(WEBSOCKET, message, args, **kws)


logging.Logger.wrapper = wrapper
logging.Logger.recv = recv
logging.Logger.send = send
logging.Logger.websocket = websocket


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Configure basic logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    return logger
