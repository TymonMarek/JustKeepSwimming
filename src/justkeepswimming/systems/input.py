import enum

import pygame
from pygame import Event, Vector2

from justkeepswimming.systems.dispatcher import Dispatcher
from justkeepswimming.utilities.log import logger
from justkeepswimming.utilities.signal import Signal


class InputActionId(enum.StrEnum):
    PLAYER_MOVE_UP = enum.auto()
    PLAYER_MOVE_DOWN = enum.auto()
    PLAYER_MOVE_LEFT = enum.auto()
    PLAYER_MOVE_RIGHT = enum.auto()
    PLAYER_TURN_LEFT = enum.auto()
    PLAYER_TURN_RIGHT = enum.auto()


class KeyboardKeyType(enum.Enum):
    W = pygame.K_w
    A = pygame.K_a
    S = pygame.K_s
    D = pygame.K_d
    Q = pygame.K_q
    E = pygame.K_e


class MouseButtonType(enum.Enum):
    LEFT = pygame.BUTTON_LEFT
    RIGHT = pygame.BUTTON_RIGHT
    MIDDLE = pygame.BUTTON_MIDDLE


class InputAction:
    def __init__(
        self,
        id: InputActionId,
        name: str,
        default_bindings: list[KeyboardKeyType | MouseButtonType],
    ) -> None:
        self.id = id
        self.name = name
        self.default_bindings = default_bindings

        self.active: bool = False
        self.__active_start_time: float = 0.0
        self.__active_bindings: int = 0

        self.on_triggered = Signal()
        self.on_reset = Signal()

    async def _activate(self) -> None:
        self.active = True
        self.__active_start_time = pygame.time.get_ticks()
        await self.on_triggered.emit()

    async def _deactivate(self) -> None:
        self.active = False
        self.__active_start_time = 0.0
        await self.on_reset.emit()

    async def binding_pressed(self) -> None:
        self.__active_bindings += 1
        if not self.active:
            await self._activate()

    async def binding_released(self) -> None:
        self.__active_bindings = max(0, self.__active_bindings - 1)
        if self.active and self.__active_bindings == 0:
            await self._deactivate()

    @property
    def active_duration(self) -> float:
        if not self.active:
            return 0.0
        return pygame.time.get_ticks() - self.__active_start_time


class KeyboardKey:
    def __init__(self, key_type: KeyboardKeyType) -> None:
        self.key_type = key_type
        self.pressed: bool = False
        self.__press_start_time: float = 0.0

        self.on_pressed = Signal()
        self.on_released = Signal()

    async def press(self):
        self.pressed = True
        self.__press_start_time = pygame.time.get_ticks()
        await self.on_pressed.emit()

    async def release(self):
        self.pressed = False
        self.__press_start_time = 0.0
        await self.on_released.emit()

    @property
    def press_duration(self) -> float:
        if not self.pressed:
            return 0.0
        return pygame.time.get_ticks() - self.__press_start_time


class Keyboard:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.keys: dict[KeyboardKeyType, KeyboardKey] = {}

        self._on_key_down = dispatcher.get_signal_for(pygame.KEYDOWN)
        self._on_key_up = dispatcher.get_signal_for(pygame.KEYUP)

        self.on_key_pressed = Signal[KeyboardKey]()
        self.on_key_released = Signal[KeyboardKey]()

        self._on_key_down.connect(self._handle_key_down_event)
        self._on_key_up.connect(self._handle_key_up_event)

    async def _get_keyboard_key(self, key_type: KeyboardKeyType) -> KeyboardKey:
        key = self.keys.get(key_type)
        if key is None:
            key = KeyboardKey(key_type)
            self.keys[key_type] = key
        return key

    async def _handle_key_down_event(self, event: Event) -> None:
        if event.key not in KeyboardKeyType:
            logger.warning(f"Unknown keyboard key: {event.key}")
            return
        key_type = KeyboardKeyType(event.key)
        key = await self._get_keyboard_key(key_type)
        await key.press()
        await self.on_key_pressed.emit(key)

    async def _handle_key_up_event(self, event: Event) -> None:
        if event.key not in KeyboardKeyType:
            logger.warning(f"Unknown keyboard key: {event.key}")
            return
        key_type = KeyboardKeyType(event.key)
        key = await self._get_keyboard_key(key_type)
        await key.release()
        await self.on_key_released.emit(key)


class MouseButton:
    def __init__(self, button_type: MouseButtonType) -> None:
        self.button_type = button_type
        self.pressed: bool = False
        self.__press_start_time: float = 0.0

        self.on_pressed = Signal()
        self.on_released = Signal()

    async def press(self):
        self.pressed = True
        self.__press_start_time = pygame.time.get_ticks()
        await self.on_pressed.emit()

    async def release(self):
        self.pressed = False
        self.__press_start_time = 0.0
        await self.on_released.emit()

    @property
    def press_duration(self) -> float:
        if not self.pressed:
            return 0.0
        return pygame.time.get_ticks() - self.__press_start_time


class Mouse:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.buttons: dict[MouseButtonType, MouseButton] = {}
        self.position: Vector2 = Vector2(0, 0)

        self._on_motion = dispatcher.get_signal_for(pygame.MOUSEMOTION)
        self._on_button_down = dispatcher.get_signal_for(pygame.MOUSEBUTTONDOWN)
        self._on_button_up = dispatcher.get_signal_for(pygame.MOUSEBUTTONUP)

        self.on_mouse_move = Signal[Vector2]()
        self.on_mouse_button_pressed = Signal[MouseButton]()
        self.on_mouse_button_released = Signal[MouseButton]()

        self._on_motion.connect(self._handle_motion_event)
        self._on_button_down.connect(self._handle_mouse_button_down_event)
        self._on_button_up.connect(self._handle_mouse_button_up_event)

    async def _handle_motion_event(self, event: Event) -> None:
        self.position = Vector2(event.pos)

    async def _get_mouse_button(self, button_type: MouseButtonType) -> MouseButton:
        button = self.buttons.get(button_type)
        if button is None:
            button = MouseButton(button_type)
            self.buttons[button_type] = button
        return button

    async def _handle_mouse_button_down_event(self, event: Event) -> None:
        if event.button not in MouseButtonType:
            logger.warning(f"Unknown mouse button: {event.button}")
            return
        button_type = MouseButtonType(event.button)
        button = await self._get_mouse_button(button_type)
        await button.press()

    async def _handle_mouse_button_up_event(self, event: Event) -> None:
        if event.button not in MouseButtonType:
            logger.warning(f"Unknown mouse button: {event.button}")
            return
        button_type = MouseButtonType(event.button)
        button = await self._get_mouse_button(button_type)
        await button.release()


class ActionManager:
    def __init__(self, keyboard: Keyboard, mouse: Mouse) -> None:
        self.actions: dict[InputActionId, InputAction] = {}

        self._key_bindings: dict[KeyboardKeyType, list[InputAction]] = {}
        self._mouse_bindings: dict[MouseButtonType, list[InputAction]] = {}

        keyboard.on_key_pressed.connect(self._on_key_pressed)
        keyboard.on_key_released.connect(self._on_key_released)

        mouse.on_mouse_button_pressed.connect(self._on_mouse_pressed)
        mouse.on_mouse_button_released.connect(self._on_mouse_released)

    def register_action(self, action: InputAction) -> None:
        self.actions[action.id] = action
        for binding in action.default_bindings:
            if isinstance(binding, KeyboardKeyType):
                self._key_bindings.setdefault(binding, []).append(action)
            else:
                self._mouse_bindings.setdefault(binding, []).append(action)

    def unregister_action(self, action: InputAction) -> None:
        self.actions.pop(action.id, None)

        for bindings in self._key_bindings.values():
            if action in bindings:
                bindings.remove(action)

        for bindings in self._mouse_bindings.values():
            if action in bindings:
                bindings.remove(action)

    async def _on_key_pressed(self, key: KeyboardKey) -> None:
        for action in self._key_bindings.get(key.key_type, []):
            await action.binding_pressed()

    async def _on_key_released(self, key: KeyboardKey) -> None:
        for action in self._key_bindings.get(key.key_type, []):
            await action.binding_released()

    async def _on_mouse_pressed(self, button: MouseButton) -> None:
        for action in self._mouse_bindings.get(button.button_type, []):
            await action.binding_pressed()

    async def _on_mouse_released(self, button: MouseButton) -> None:
        for action in self._mouse_bindings.get(button.button_type, []):
            await action.binding_released()


class Input:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.keyboard = Keyboard(dispatcher)
        self.mouse = Mouse(dispatcher)
        self.action_manager = ActionManager(self.keyboard, self.mouse)
