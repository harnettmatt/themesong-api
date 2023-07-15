import random
import string
from typing import Dict

from fastapi import Request


def get_query_params_as_dict(request: Request) -> Dict[str, str]:
    request_args = {}
    for _ in str(request.query_params).split("&"):
        [key, value] = _.split("=")
        request_args[key] = str(value)

    return request_args


def generate_auth_state() -> str:
    return "".join(random.choices(string.ascii_letters, k=16))
