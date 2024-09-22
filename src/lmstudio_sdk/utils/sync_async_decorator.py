import functools
import asyncio
from typing import Callable, TypeVar, Union, Any, Awaitable, Tuple


T = TypeVar("T")


# TODO: this file contains possibly the worst hack I have ever written
# document this for the next person who has to deal with it
# I'm sorry


# this whole hack is almost workaroundable in most places (RPC calls)
# because you could just return the call to self._port.send_rpc, and then
# the user awaiting it would await on the RPC call... but then we don't
# get to postprocess the result. damn it!
class AsyncCallable:
    """
    Because functions are declared with def in this design pattern, asyncio.iscoroutinefunction
    does not know at runtime that nested async function calls are async, so we wrap them to indicate
    that they are async. It's a bit of a hack, but it works.
    """

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


# checks whether we need to await the target
def is_async_callable(obj):
    """Checks whether we need to await the target."""
    return asyncio.iscoroutinefunction(obj) or isinstance(obj, AsyncCallable)


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
                method_args = {}

            # handle nested decorated calls
            if hasattr(target_method, "is_sync_async_decorated"):
                result = await target_method(**method_args)
            # handle top-level async calls
            elif is_async_callable(target_method):
                result = await target_method(**method_args)
            # welp guess it isn't async
            else:
                result = target_method(**method_args)

            # processor can in theory be async but really try not to do this
            if is_async_callable(process_result):
                return await process_result(result)
            return process_result(result)

        # sync wrapper
        @functools.wraps(func)
        def sync_wrapper(self, target_method, *args, **kwargs):
            # output of function is a dictionary of named arguments to pass to the target method
            method_args = func(self, *args, **kwargs)
            if not isinstance(method_args, dict):
                method_args = {}

            # handle nested decorated calls
            if hasattr(target_method, "is_sync_async_decorated"):
                result = target_method(**method_args)
            # handle top-level async calls, which should never happen because this is a sync wrapper
            elif is_async_callable(target_method):
                raise RuntimeError(f"Cannot call async method '{obj_method}' in a synchronous context")
            # business as usual
            else:
                result = target_method(**method_args)

            return process_result(result)

        # the wrapper proper
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # determine target method
            target_method = get_target_and_method(self, obj_method)

            # determine whether to wrap in async or sync based on the target method
            if is_async_callable(target_method) or hasattr(target_method, "is_sync_async_decorated"):
                return AsyncCallable(lambda: async_wrapper(self, target_method, *args, **kwargs))
            return sync_wrapper(self, target_method, *args, **kwargs)

        wrapper.is_sync_async_decorated = True
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
