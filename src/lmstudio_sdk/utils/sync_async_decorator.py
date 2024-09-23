import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar, Tuple, Union
from .logger import get_logger
from .utils import pretty_print

logger = get_logger(__name__)


T = TypeVar("T")


def sync_async_decorator(
    obj_method: Union[str, Tuple[str, str]], process_result: Callable[[Any], T] = lambda x: x
) -> Callable[[Callable[..., Any]], Callable[..., Union[T, Awaitable[T]]]]:
    """
    This is a beautiful hack that allows broad reuse of the same logic for both synchronous and asynchronous
    calls, whereas typically (cf. discussion in the link below) the codebase would need to be mostly duplicated.
    Since most functions require only one call to an RPC/channel endpoint, we can use this decorator to wrap this
    call in a function that can be awaited if necessary.

    In most cases this is almost unnecessary, because we could just return the call to `self._port.send_rpc`, and
    then the user awaiting it would await on the RPC call... but then we wouldn't get to postprocess the result.
    Incidentally, the postprocessing code is often pretty cursed (see: everywhere we depend on the `channel_id`,
    which requires convoluted postprocessing logic) because of this design pattern. I don't really like it,
    but it's what we have to work with.

    To write a function using this decorator, pass the method to `obj_method` and a callback to the postprocessing
    function to `process_result`. `obj_method` handles multiple cases: if it's a string, we assume it's a method
    on `self._port` first, then `self`. If it's a tuple, we assume it's a method on a different object; pass the
    object (or name of field on `self`) and method name as a tuple. `process_result` should be a single-parameter
    Callable, either a lambda or a predefined handler, and both should expect dicts.

    The result of calling the bare function should be a dictionary of named arguments to pass to the target method.
    If you need to pass references to internal variables, this can be done using the `extra` parameter, supported by
    all relevant backend methods; this will pass the content of the `extra` dictionary to the `process_result` callback
    for whatever you need to do with it. This API will probably change because this is a terrible design pattern.

    https://discuss.python.org/t/how-can-async-support-dispatch-between-sync-and-async-variants-of-the-same-code/15014
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Union[T, Awaitable[T]]]:
        # async wrapper
        @functools.wraps(func)
        async def async_wrapper(self, target_method, *args, **kwargs):
            # output of function is a dictionary of named arguments to pass to the target method
            method_args = func(self, *args, **kwargs)
            if not isinstance(method_args, dict):
                logger.warning(f"Expected dictionary from {func}, got {type(method_args)}: {method_args}")
                method_args = {}

            logger.wrapper(f"Calling async method '{target_method}' with inner args {method_args}")
            result = await target_method(**method_args)
            logger.wrapper(f"Async wrapper for {target_method} received result:\n{pretty_print(result)}")

            return process_result(result)

        # sync wrapper
        @functools.wraps(func)
        def sync_wrapper(self, target_method, *args, **kwargs):
            # output of function is a dictionary of named arguments to pass to the target method
            method_args = func(self, *args, **kwargs)
            if not isinstance(method_args, dict):
                logger.warning(f"Expected dictionary from {func}, got {type(method_args)}: {method_args}")
                method_args = {}

            logger.wrapper(f"Calling sync method '{target_method}' with inner args {method_args}")
            result = target_method(**method_args)
            logger.wrapper(f"Sync wrapper for {target_method} received result:\n{pretty_print(result)}")

            return process_result(result)

        # the wrapper proper
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # determine target method
            target_method = get_target_and_method(self, obj_method)

            # determine whether to wrap in async or sync based on the target method
            is_async = (
                (hasattr(self, "is_async") and self.is_async())
                or (hasattr(target_method, "is_async") and target_method.is_async(target_method.__self__))
                or asyncio.iscoroutinefunction(target_method)
            )
            logger.wrapper(f"{self}: calling {'async' if is_async else 'sync'} '{target_method}' \
                           with outer args {args} and outer kwargs\n{pretty_print(kwargs)}")

            if is_async:
                return async_wrapper(self, target_method, *args, **kwargs)
            return sync_wrapper(self, target_method, *args, **kwargs)

        # recursively determine whether the target method is async by asking the target method's target method
        def is_async(self):
            target_method = get_target_and_method(self, obj_method)
            return (
                target_method.is_async(self)
                if hasattr(target_method, "is_async")
                else asyncio.iscoroutinefunction(target_method)
            )

        wrapper.is_async = is_async
        return wrapper

    return decorator


# handle different types of obj_method so we can specify exactly what to call
def get_target_and_method(self, obj_method):
    # if obj_method is a string, we assume it's a method on self._port first, then self
    if isinstance(obj_method, str):
        if hasattr(self, "_port") and hasattr(self._port, obj_method):
            return getattr(self._port, obj_method)
        return getattr(self, obj_method)

    # if obj_method is a tuple, we assume it's a method on a different object
    elif isinstance(obj_method, tuple):
        obj_name, method_name = obj_method

        # if obj_name is not a string, we assume it's a reference to an object
        if not isinstance(obj_name, str):
            return getattr(obj_name, method_name)
        # if obj_name is a string, we assume it's a reference to a field on self
        return getattr(getattr(self, obj_name), method_name)
    else:
        raise ValueError(f"Invalid obj_method type: {type(obj_method)}")
