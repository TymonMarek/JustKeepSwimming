from enum import Enum
import time
from typing import List

import pygame

from clock import Tick
from emitter import Emitter

class KeyCode(Enum):
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
    def __init__(self, name: str, description: str, keycode: KeyCode) -> None:
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
        self.pressed.listen(lambda tick, event: self.__set_state(True))
        self.released.listen(lambda tick, event: self.__set_state(False))


class KeyMap:
    def __init__(self) -> None:
        self.bindings: List[KeyBind] = []

    def bind(self, name: str, description: str, keycode: KeyCode) -> KeyBind:
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
        self.pressed.listen(lambda tick, event: self.__set_state(True))
        self.released.listen(lambda tick, event: self.__set_state(False))


class MouseButtons:
    def __init__(self) -> None:
        self.left = MouseButton()
        self.middle = MouseButton()
        self.right = MouseButton()

    async def on_pressed(self, tick: Tick, event: pygame.event.Event) -> None:
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
    def __init__(self) -> None:
        self.delta = pygame.Vector2(0, 0)
    
    def on_scroll(self, tick: Tick, event: pygame.event.Event) -> None:
        self.delta = pygame.Vector2(event.x, event.y)


class Mouse:
    def __init__(self) -> None:
        self.buttons = MouseButtons()
        self.scroll = MouseScroll()
        self.position = pygame.Vector2()
        self.delta = pygame.Vector2()
        self.direction = pygame.Vector2()

    def on_mouse_moved(self, tick: Tick, event: pygame.event.Event) -> None:
        self.delta = pygame.Vector2(pygame.mouse.get_rel())
        self.position = pygame.Vector2(pygame.mouse.get_pos())
        self.direction = self.delta.normalize() if self.delta.magnitude() > 0 else pygame.Vector2(0, 0)


class Input:
    def __init__(self) -> None:
        self.keyboard = Keyboard()
        self.mouse = Mouse()

