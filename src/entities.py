from typing import List
from pygame import Vector2
from clock import Tick
from sprites import Sprite

all: List["Entity"] = []

class Entity:
    def __init__(self) -> None:
        self.sprite = Sprite()

        self.max_velocity = Vector2(200, 200)
        self.acceleration: Vector2 = Vector2()
        self.friction: float = 0.00
        self.velocity: Vector2 = Vector2()
        
        self.wish_direction: Vector2 = Vector2()
        self.force = Vector2(5, 5)

        self.__post_init__()

    def __post_init__(self) -> None:
        all.append(self)

    def update(self, tick: Tick):
        wish_direction = self.wish_direction.normalize() if self.wish_direction.magnitude() > 0 else Vector2(0, 0)
        self.acceleration = Vector2(wish_direction.x * self.force.x, wish_direction.y * self.force.y)
        self.velocity = self.acceleration
        self.velocity = self.velocity * (1 - self.friction)
        self.sprite.position = (self.sprite.position + self.velocity) * tick.delta_time