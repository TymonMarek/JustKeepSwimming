from dataclasses import dataclass, field

from pygame import Vector2
from justkeepswimming.ecs import Component


@dataclass
class Transform(Component):
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    rotation: float = 0.0
    size: Vector2 = field(default_factory=lambda: Vector2(1, 1))
    anchor: Vector2 = field(default_factory=lambda: Vector2(0.5, 0.5))
