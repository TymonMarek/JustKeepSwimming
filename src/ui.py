from pygame import Surface
import pygame
from pygame_gui import UIManager
from clock import Tick
from render import Window

class UI:
    def __init__(self, window: Window) -> None:
        self.manager = UIManager((int(window.size.x), int(window.size.y)))

    def update(self, tick: Tick) -> None:
        self.manager.update(tick.delta_time)

    def process(self, event: pygame.event.Event) -> None:
        self.manager.process_events(event)

    def draw(self, target: Surface) -> None:
        self.manager.draw_ui(target)
        

