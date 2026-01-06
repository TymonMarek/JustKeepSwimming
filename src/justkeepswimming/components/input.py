from dataclasses import dataclass, field

from pygame import Vector2

from justkeepswimming.ecs import Component


@dataclass
class PlayerLinearMovementInputComponent(Component):
    thrust: Vector2 = field(default_factory=lambda: Vector2(0, 0))


@dataclass
class PlayerAngularMovementInputComponent(Component):
    torque: float = 0.0
