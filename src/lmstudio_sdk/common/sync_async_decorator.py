import functools
import asyncio
from typing import Callable, TypeVar, Union, Any, Awaitable, Tuple


T = TypeVar("T")


# TODO: this file contains possibly the worst hack I have ever written
# document this for the next person who has to deal with it
# I'm sorry


class AsyncCallable:
    def __init__(self, func):
        self.func = func

    def __await__(self):
        return self._await().__await__()

    async def _await(self):
        result = self.func
        if asyncio.iscoroutine(result):
            result = await result
        elif callable(result):
            result = result()
            if asyncio.iscoroutine(result):
                result = await result
        return result


def is_async_callable(obj):
    return asyncio.iscoroutinefunction(obj) or isinstance(obj, AsyncCallable)


def sync_async_decorator(
    obj_method: Union[str, Tuple[str, str]], process_result: Callable[[Any], T] = lambda x: x
) -> Callable[[Callable[..., Any]], Callable[..., Union[T, Awaitable[T]]]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Union[T, Awaitable[T]]]:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            method_args = func(self, *args, **kwargs)
            if not isinstance(method_args, dict):
                method_args = {}
            target_obj, target_method = get_target_and_method(self, obj_method)

            # Handle nested decorated calls
            if hasattr(target_method, "is_sync_async_decorated"):
                result = await target_method(**method_args)
            elif is_async_callable(target_method):
                result = await target_method(**method_args)
            else:
                result = target_method(**method_args)

            if is_async_callable(process_result):
                return await process_result(result)
            return process_result(result)

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            method_args = func(self, *args, **kwargs)
            if not isinstance(method_args, dict):
                method_args = {}
            target_obj, target_method = get_target_and_method(self, obj_method)

            if hasattr(target_method, "is_sync_async_decorated"):
                result = target_method(**method_args)
            elif is_async_callable(target_method):
                raise RuntimeError(f"Cannot call async method '{obj_method}' in a synchronous context")
            else:
                result = target_method(**method_args)

            return process_result(result)

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            target_obj, target_method = get_target_and_method(self, obj_method)
            if is_async_callable(target_method) or hasattr(target_method, "is_sync_async_decorated"):
                return AsyncCallable(lambda: async_wrapper(self, *args, **kwargs))
            return sync_wrapper(self, *args, **kwargs)

        wrapper.is_sync_async_decorated = True
        return wrapper

    return decorator


def get_target_and_method(self, obj_method):
    if isinstance(obj_method, str):
        if hasattr(self, "_port") and hasattr(self._port, obj_method):
            return self._port, getattr(self._port, obj_method)
        return self, getattr(self, obj_method)
    elif isinstance(obj_method, tuple):
        obj_name, method_name = obj_method
        target_obj = getattr(self, obj_name)
        return target_obj, getattr(target_obj, method_name)
    else:
        raise ValueError(f"Invalid obj_method type: {type(obj_method)}")
