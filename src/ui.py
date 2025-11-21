import pygame
from pygame_gui import UIManager
from clock import Tick
from render import Window

class UI:
    """An abstraction of the `pygame_gui` library that allows for integration with the codebase.
    """
    def __init__(self, window: Window) -> None:
        self.manager = UIManager((int(window.size.x), int(window.size.y)))
        self.window = window

    async def update(self, tick: Tick) -> None:
        self.manager.update(tick.delta_time)

    def process(self, event: pygame.event.Event) -> None:
        self.manager.process_events(event)

    async def render(self) -> None:
        self.manager.draw_ui(self.window.surface)
        

