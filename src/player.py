from typing import Dict
from pygame import Color, Vector2
from clock import Tick
from entities import Entity
from input import KeyBind, KeyCode, KeyMap

class Player:
    """An object representing the player. Handles input, entity and rendering.
    """
    def __init__(self, keymap: KeyMap) -> None:
        self.entity = Entity()
        self.entity.sprite.size = Vector2(100, 100)
        self.entity.sprite.position = Vector2(300, 300)
        self.entity.sprite.surface.fill(Color(255, 255, 255))
        self.input_map: Dict[KeyBind, Vector2] = {
            keymap.bind("Move upwards", "Moves the player's character upwards", KeyCode.W): Vector2(0, -1),
            keymap.bind("Move left", "Moves the player's character to the left", KeyCode.A): Vector2(-1, 0),
            keymap.bind("Move downwards", "Moves the player's character downwards", KeyCode.S): Vector2(0, 1),
            keymap.bind("Move right", "Moves the player's character to the right", KeyCode.D): Vector2(1, 0)
        }

    def update(self, tick: Tick) -> None:
        """Updates the wish direction based on the keys that are currently pressed.

        Args:
            tick (Tick): Information about the current tick.
        """
        wish_direction = Vector2(0, 0)
        for key, force in self.input_map.items():
            if key.active:
                wish_direction += force
        self.entity.wish_direction = wish_direction
