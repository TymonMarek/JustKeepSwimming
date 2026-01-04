from dataclasses import dataclass
from pygame import Vector2


@dataclass
class TransformData:
    position: Vector2
    rotation: float
    scale: Vector2
    anchor: Vector2 = Vector2(0.5, 0.5)
