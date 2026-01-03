from dataclasses import dataclass, field

from pygame import Vector2
from justkeepswimming.ecs import Component


@dataclass
class MovementInput(Component):
    wish_direction: Vector2 = field(default_factory=lambda: Vector2(0, 0))
