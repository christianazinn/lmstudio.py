import base64
import json
import secrets
from typing import Any, Coroutine, Dict, Optional, TypeVar, Union

lms_default_ports = [1234]


def generate_random_base64(byte_length: int) -> str:
    random_bytes = secrets.token_bytes(byte_length)
    return base64.b64encode(random_bytes).decode("utf-8")


def number_to_checkbox_numeric(
    self,
    value: Optional[float],
    unchecked_value: float,
    value_when_unchecked: float,
) -> Optional[Dict[str, Union[bool, float]]]:
    if value is None:
        return None
    if value == unchecked_value:
        return {"checked": False, "value": value_when_unchecked}
    if value != unchecked_value:
        return {"checked": True, "value": value}


# TODO: can you change indent on the fly?
def pretty_print(obj):
    """Pretty prints the object."""
    try:
        return json.dumps(obj, indent=2, default=lambda x: str(x))
    except Exception:
        return obj


def pretty_print_error(obj):
    try:
        obj["stack"] = obj.get("stack", "").split("\n")
        return pretty_print(obj)
    except Exception:
        return obj


def _assert(condition: bool, message: str, info: str, logger):
    if not condition:
        logger.error(message, info)
        raise ValueError(message, info)


class RPCError(Exception):
    """Raised when an RPC call fails."""
    pass


class ChannelError(Exception):
    """Raised when an error occurs in the channel."""
    pass


T = TypeVar("T")
LiteralOrCoroutine = Union[T, Coroutine[Any, Any, T]]
