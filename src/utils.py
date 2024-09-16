from pydantic import BaseModel, ValidationError
from typing import Any


def validate(obj: Any, model: type[BaseModel]) -> bool:
    try:
        model.model_validate(obj)
        return True
    except ValidationError:
        return False
