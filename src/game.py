import sys
import pygame

from stage import Stage

pygame.init()

from clock import Clock
from events import Events
from input import Input
from player import Player
from window import Window


class Game:
    """The game object represents the main game logic. It is a container for all the game's components, controls the execution cycle and binds emitters to their respective handlers.
    """
    def __init__(self) -> None:
        self.clock = Clock()
        self.events = Events()
        self.input = Input()
        self.window = Window()
        self.player = Player(self.input.keyboard.keymap)
        self.stage = Stage(self.player, self.window)
        self.running: bool = False
        self.__post_init__()

    def __post_init__(self) -> None:
        ## Bind Pygame input events to input event handlers.
        self.events.bind(pygame.MOUSEBUTTONDOWN, self.input.mouse.buttons.on_pressed)
        self.events.bind(pygame.MOUSEBUTTONUP, self.input.mouse.buttons.on_released)
        self.events.bind(pygame.MOUSEWHEEL, self.input.mouse.scroll.on_scroll)
        self.events.bind(pygame.MOUSEMOTION, self.input.mouse.on_mouse_moved)
        self.events.bind(pygame.KEYDOWN, self.input.keyboard.on_key_pressed)
        self.events.bind(pygame.KEYUP, self.input.keyboard.on_key_released)
        self.events.bind(pygame.QUIT, lambda tick, event: self.quit())

    async def start(self) -> None:
        """Starts the game by running the main game loop.
        """
        await self.stage.load_scene("default")
        try:
            await self._game_loop()
        except KeyboardInterrupt:
            self.quit()

    def quit(self) -> None:
        """Stops the game loop and exits the game after the current tick.
        """
        self.running = False

    async def _game_loop(self) -> None:
        """Starts the main game loop, which runs until `Game.quit()` is called. All tick updates are handled here. 
        """
        self.running = True
        while self.running:
            self.window.surface.fill((0, 0, 0))
            tick = await self.clock.tick()
            await self.events.tick(tick)
            await self.stage.update(tick)
            self.window.flip()
        pygame.quit()
        sys.exit(0)
