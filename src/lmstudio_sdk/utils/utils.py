from base64 import b64encode
from secrets import token_bytes


lms_default_ports = [1234]


def generate_random_base64(byte_length: int) -> str:
    random_bytes = token_bytes(byte_length)
    return b64encode(random_bytes).decode("utf-8")
