from dataclasses import dataclass

from justkeepswimming.modules.clock import Clock
from justkeepswimming.modules.window import Window
from justkeepswimming.modules.dispatcher import Dispatcher


@dataclass(frozen=True)
class GameContext:
    clock: Clock
    window: Window
    dispatcher: Dispatcher
