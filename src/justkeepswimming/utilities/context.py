from dataclasses import dataclass

from justkeepswimming.systems.clock import Clock
from justkeepswimming.systems.dispatcher import Dispatcher
from justkeepswimming.systems.window import Window


@dataclass(frozen=True)
class EngineContext:
    clock: Clock
    window: Window
    dispatcher: Dispatcher
