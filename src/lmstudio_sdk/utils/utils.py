import json
from base64 import b64encode
from secrets import token_bytes
from typing import Dict, Optional, Union


lms_default_ports = [1234]


def generate_random_base64(byte_length: int) -> str:
    random_bytes = token_bytes(byte_length)
    return b64encode(random_bytes).decode("utf-8")


def number_to_checkbox_numeric(
    self, value: Optional[float], unchecked_value: float, value_when_unchecked: float
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


class RPCError(Exception):
    pass


class ChannelError(Exception):
    pass
