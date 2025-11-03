from typing import Any, Callable, Generic, List, ParamSpec
import inspect

CallbackParams = ParamSpec("CallbackParams")

class Emitter(Generic[CallbackParams]):
    def __init__(self) -> None:
        self.observers: List[Observer[CallbackParams]] = []

    def listen(self, callback: Callable[CallbackParams, Any]):
        observer = Observer[CallbackParams](callback)
        self.observers.append(observer)
        return observer

    async def emit(self, *args: CallbackParams.args, **kwargs: CallbackParams.kwargs):
        for observer in self.observers:
            if inspect.iscoroutinefunction(observer.callback):
                await observer.callback.__call__(args, kwargs)
            else:
                observer.callback.__call__(args, kwargs)


class Observer(Generic[CallbackParams]):
    def __init__(self, callback: Callable[CallbackParams, Any]) -> None:
        self.callback = callback