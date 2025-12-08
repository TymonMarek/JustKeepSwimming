from typing import Any, Awaitable, Callable, Generic, List, ParamSpec
import inspect
import asyncio

CallbackParams = ParamSpec("CallbackParams")

type CallBackType[**Params] = Callable[Params, Awaitable[Any] | None]

class Emitter(Generic[CallbackParams]):
    """An event emitter that allows observers to listen for and respond to events via a callback.

    Args:
        Generic (ParamSpec): A generic parameter specification for the callback parameters.
    """
    def __init__(self) -> None:
        self.observers: List[Observer[CallbackParams]] = []

    def observe(self, callback: CallBackType[CallbackParams]) -> "Observer[CallbackParams]":
        """Registers a callback to be invoked when an event is emitted.

        Args:
            callback (Callable[CallbackParams, Any]): The callback function that is executed when the emitter emits.

        Returns:
            Observer: The observer instance that was created for the callback.
        """
        observer = Observer(self, callback)
        self.observers.append(observer)
        return observer
    
    def once(self, callback: CallBackType[CallbackParams]) -> "Observer[CallbackParams]":
        """Registers a callback to be invoked only once when an event is emitted.

        Args:
            callback (Callable[CallbackParams, Any]): The callback function that is executed when the emitter emits.
        Returns:
            Observer: The observer instance that was created for the callback. Keep in mind, this observer will disconnect itself after the first invocation, so make sure to check its `connected` property if you plan to use manually disconnect it later.
        """
        async def wrapper(*args: CallbackParams.args, **kwargs: CallbackParams.kwargs) -> None:
            if inspect.iscoroutinefunction(callback):
                await callback.__call__(*args, **kwargs)
            else:
                callback.__call__(*args, **kwargs)
            observer.disconnect()
        
        observer = self.observe(wrapper)
        return observer
    
    async def wait(self) -> None:
        """Waits for the next emission of an event. This method will block until `Emitter.emit()` is called.
        """
        future = asyncio.get_event_loop().create_future()

        def resolver(*args: CallbackParams.args, **kwargs: CallbackParams.kwargs) -> None:
            if not future.done():
                future.set_result(None)

        self.once(resolver)
        await future

    async def emit(self, *args: CallbackParams.args, **kwargs: CallbackParams.kwargs):
        """Emits an event, invoking all registered callbacks with the provided arguments. This method will block until all callbacks have been executed.
        """
        for observer in self.observers:
            if inspect.iscoroutinefunction(observer.callback):
                await observer.callback.__call__(*args, **kwargs)
            else:
                observer.callback.__call__(*args, **kwargs)

    
    async def emit_nonblocking(self, *args: CallbackParams.args, **kwargs: CallbackParams.kwargs):
        """Emits an event, invoking all registered callbacks with the provided arguments. This method will not block the execution and will schedule
        async callbacks to run concurrently without waiting for them to complete."""
        tasks: List[asyncio.Task[None]] = []
        
        for observer in self.observers:
            if inspect.iscoroutinefunction(observer.callback):
                tasks.append(asyncio.create_task(observer.callback.__call__(*args, **kwargs)))
            else:
                observer.callback.__call__(*args, **kwargs)

    async def emit_waiting(self, *args: CallbackParams.args, **kwargs: CallbackParams.kwargs):
        """Emits an event, invoking all registered callbacks with the provided arguments. 
        This method will run all async callbacks concurrently and wait for all of them to complete before continuing."""
        tasks: List[asyncio.Task[None]] = []
        
        for observer in self.observers:
            if inspect.iscoroutinefunction(observer.callback):
                tasks.append(asyncio.create_task(observer.callback.__call__(*args, **kwargs)))
            else:
                observer.callback.__call__(*args, **kwargs)

        if tasks:
            await asyncio.gather(*tasks)


class Observer(Generic[CallbackParams]):
    """A object which stores the callback that is executed when its corresponding emitter emits.
    Do not create this object directly; use Emitter.observe instead.

    Args:
        Generic (CallbackParams): A generic parameter specification for the callback parameters, specified by the emitter.
    """
    def __init__(self, emitter: Emitter[CallbackParams], callback: CallBackType[CallbackParams]) -> None:
        self.callback = callback
        self.connected = True
        self.__emitter = emitter

    def disconnect(self) -> None:
        """Disconnect the `Observer` from the `Emitter`. This causes the `Observer` to no longer fire from `Emitter.emit()`
        """
        if self in self.__emitter.observers:
            self.__emitter.observers.remove(self)
        self.connected = False
