from dataclasses import dataclass, field

from pygame import Vector2

from justkeepswimming.ecs import Component


@dataclass
class LinearPhysicsComponent(Component):
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    acceleration: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    thrust: float = 3000.0
    max_velocity: float = 2000.0
    drag: float = 0.6


@dataclass
class AngularPhysicsComponent(Component):
    angular_velocity: float = 0.0
    angular_acceleration: float = 0.0
    torque: float = 500.0
    max_angular_velocity: float = 100.0
    angular_drag: float = 0.6


@dataclass
class TransformComponent(Component):
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    rotation: float = 0.0
    size: Vector2 = field(default_factory=lambda: Vector2(1, 1))
    anchor: Vector2 = field(default_factory=lambda: Vector2(0.5, 0.5))

    @property
    def up(self) -> Vector2:
        return Vector2(0, -1).rotate(self.rotation)

    @property
    def right(self) -> Vector2:
        return Vector2(1, 0).rotate(self.rotation)
