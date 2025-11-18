from typing import Any, Callable, Generic, List, ParamSpec
import inspect

CallbackParams = ParamSpec("CallbackParams")

class Emitter(Generic[CallbackParams]):
    """An event emitter that allows observers to listen for and respond to events via a callback.

    Args:
        Generic (ParamSpec): A generic parameter specification for the callback parameters.
    """
    def __init__(self) -> None:
        self.observers: List[Observer[CallbackParams]] = []

    def listen(self, callback: Callable[CallbackParams, Any]) -> "Observer[CallbackParams]":
        """Registers a callback to be invoked when an event is emitted.

        Args:
            callback (Callable[CallbackParams, Any]): The callback function that is executed when the emitter emits.

        Returns:
            Observer: The observer instance that was created for the callback.
        """
        observer = Observer[CallbackParams](callback)
        self.observers.append(observer)
        return observer

    async def emit(self, *args: CallbackParams.args, **kwargs: CallbackParams.kwargs):
        """Emits an event, invoking all registered callbacks with the provided arguments. This method will block until all callbacks have been executed.
        """
        for observer in self.observers:
            if inspect.iscoroutinefunction(observer.callback):
                await observer.callback.__call__(*args, **kwargs)
            else:
                observer.callback.__call__(*args, **kwargs)


class Observer(Generic[CallbackParams]):
    """A object which stores the callback that is executed when its corresponding emitter emits.
    Do not create this object directly; use Emitter.listen instead.

    Args:
        Generic (CallbackParams): A generic parameter specification for the callback parameters, specified by the emitter.
    """
    def __init__(self, callback: Callable[CallbackParams, Any]) -> None:
        self.callback = callback