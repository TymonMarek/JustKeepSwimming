from enum import Enum
import time
from typing import List

import pygame

from clock import Tick
from emitter import Emitter

class KeyCode(Enum):
    """An enum mapping of keys to their pygame IDs, the keys being a human readable name.
    """
    W = pygame.K_w
    A = pygame.K_a
    S = pygame.K_s
    D = pygame.K_d
    Up = pygame.K_UP
    Down = pygame.K_DOWN
    Left = pygame.K_LEFT
    Right = pygame.K_RIGHT
    Space = pygame.K_SPACE
    Enter = pygame.K_RETURN
    Escape = pygame.K_ESCAPE


class KeyBind:
    """A binding of a key to an action.
    This class should not be instantiated directly, but rather through `KeyMap.bind()`.
    """
    def __init__(self, name: str, description: str, keycode: KeyCode) -> None:
        """The constructor method that creates and binds a `KeyBind`.
        The key bind will emit events when the key is pressed or released, as well as contain timing information for the last state.

        Args:
            name (str): A human readable name for the key bind.
            description (str): A human readable description for the key bind.
            keycode (KeyCode): The enum value of the key to bind.
        """
        self.name = name
        self.description = description
        self.keycode = keycode
        self.pressed = Emitter[Tick, pygame.event.Event]()
        self.released = Emitter[Tick, pygame.event.Event]()
        self.active = False
        self.since = time.time()
        self.__post_init__()

    def __set_state(self, state: bool) -> None:
        if self.active == state:
            return
        self.active = state
        self.since = time.time()
    
    def __post_init__(self) -> None:
        self.pressed.observe(lambda tick, event: self.__set_state(True))
        self.released.observe(lambda tick, event: self.__set_state(False))


class KeyMap:
    """A handler that stores and fires `KeyBind` objects that are associated with them.
    """
    def __init__(self) -> None:
        self.bindings: List[KeyBind] = []

    def bind(self, name: str, description: str, keycode: KeyCode) -> KeyBind:
        """Binds a new key to the key map.

        Args:
            name (str): A human readable name for the key map.
            description (str): A human readable description for the key map.
            keycode (KeyCode): A keycode enum value to bind.

        Returns:
            KeyBind: A key bind object that was created and added to the key map.
        """
        key_bind = KeyBind(name, description, keycode)
        self.bindings.append(key_bind)
        return key_bind
   
    async def on_key_pressed(self, tick: Tick, event: pygame.event.Event) -> None:
        for keybinding in self.bindings:
            if event.key == keybinding.keycode.value:
                await keybinding.pressed.emit(tick, event)

    async def on_key_released(self, tick: Tick, event: pygame.event.Event) -> None:
        for keybinding in self.bindings:
            if event.key == keybinding.keycode.value:
                await keybinding.released.emit(tick, event)


class Keyboard:
    """A handler for keyboard input.
    Contains a `KeyMap` that can be used to bind keys to actions. This keymap can be accessed and modified directly, or swapped out for another one.
    """
    def __init__(self) -> None:
        self.keymap: KeyMap = KeyMap()

    async def on_key_pressed(self, tick: Tick, event: pygame.event.Event) -> None:
        if not self.keymap:
            return
        await self.keymap.on_key_pressed(tick, event)

    async def on_key_released(self, tick: Tick, event: pygame.event.Event) -> None:
        if not self.keymap:
            return
        await self.keymap.on_key_released(tick, event)


class MouseButton:
    """An object that represents a button on a mouse. Similar to `KeyBind` it contains `Emitter`s and timing information based on the input into the mouse.
    """
    def __init__(self) -> None:
        self.pressed = Emitter[Tick, pygame.event.Event]()
        self.released = Emitter[Tick, pygame.event.Event]()
        self.active = False
        self.since = time.time()
        self.__post_init__()

    def __set_state(self, state: bool) -> None:
        if self.active == state:
            return
        self.active = state
        self.since = time.time()
    
    def __post_init__(self) -> None:
        self.pressed.observe(lambda tick, event: self.__set_state(True))
        self.released.observe(lambda tick, event: self.__set_state(False))


class MouseButtons:
    """A container for `MouseButton`s that stores the different mouse buttons with a human readable index.
    """
    def __init__(self) -> None:
        self.left = MouseButton()
        """Represents the left mouse button."""
        self.middle = MouseButton()
        """Represents the button that is pressed by clicking the scroll wheel."""
        self.right = MouseButton()
        """Represents the right mouse button."""

    async def on_pressed(self, tick: Tick, event: pygame.event.Event) -> None:
        self.right
        left_button_pressed, middle_button_pressed, right_button_pressed = pygame.mouse.get_pressed(num_buttons=3)
        if left_button_pressed and not self.left.active:
            await self.left.pressed.emit(tick, event)
        if middle_button_pressed and not self.middle.active:
            await self.middle.pressed.emit(tick, event)
        if right_button_pressed and not self.right.active:
            await self.right.pressed.emit(tick, event)

    async def on_released(self, tick: Tick, event: pygame.event.Event) -> None:
        left_button_pressed, middle_button_pressed, right_button_pressed = pygame.mouse.get_pressed(num_buttons=3)
        if not left_button_pressed and self.left.active:
            await self.left.pressed.emit(tick, event)
        if not middle_button_pressed and self.middle.active:
            await self.middle.pressed.emit(tick, event)
        if not right_button_pressed and self.right.active:
            await self.right.pressed.emit(tick, event)


class MouseScroll:
    """An object representing the scroll wheel on a mouse.
    """
    def __init__(self) -> None:
        self.delta = pygame.Vector2(0, 0)
        """Represents the amount the scroll wheel has moved since the last update."""
    
    def on_scroll(self, tick: Tick, event: pygame.event.Event) -> None:
        self.delta = pygame.Vector2(event.x, event.y)


class Mouse:
    """A handler and container for mouse input.
    """
    def __init__(self) -> None:
        self.buttons = MouseButtons()
        self.scroll = MouseScroll()
        self.position = pygame.Vector2()
        self.delta = pygame.Vector2()
        self.direction = pygame.Vector2()
        self.moved = Emitter[Tick, pygame.event.Event]()

    async def on_mouse_moved(self, tick: Tick, event: pygame.event.Event) -> None:
        self.delta = pygame.Vector2(pygame.mouse.get_rel())
        self.position = pygame.Vector2(pygame.mouse.get_pos())
        self.direction = self.delta.normalize() if self.delta.magnitude() > 0 else pygame.Vector2(0, 0)
        await self.moved.emit(tick, event)


class Input:
    """A container class for all input handlers, such as keyboard and mouse.
    """
    def __init__(self) -> None:
        self.keyboard = Keyboard()
        self.mouse = Mouse()

