import json
from base64 import b64encode
from secrets import token_bytes


lms_default_ports = [1234]


def generate_random_base64(byte_length: int) -> str:
    random_bytes = token_bytes(byte_length)
    return b64encode(random_bytes).decode("utf-8")


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
