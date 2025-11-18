from typing import List
from pygame import Vector2
from clock import Tick
from sprites import Sprite

all: List["Entity"] = []

def clamp(n: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(n, max_value))

class Entity:
    """Base class for all entities in the game world.
    """
    def __init__(self) -> None:
        self.sprite = Sprite()

        self.max_velocity = Vector2(1500, 1500)
        self.acceleration: Vector2 = Vector2()
        self.velocity: Vector2 = Vector2()
        
        self.wish_direction: Vector2 = Vector2()
        self.force = Vector2(2, 2)
        self.efficiency = 0.995

        self.__post_init__()

    def __post_init__(self) -> None:
        all.append(self)
    
    def update(self, tick: Tick):
        """A function that will run every frame. This function contains all physics calculations.

        Args:
            tick (Tick): _description_
        """
        self.acceleration = Vector2(self.wish_direction.x * self.force.x, self.wish_direction.y * self.force.y)
        self.velocity += self.acceleration
        self.velocity = self.velocity * self.efficiency
        self.velocity = Vector2(clamp(self.velocity.x, -self.max_velocity.x, self.max_velocity.x), clamp(self.velocity.y, -self.max_velocity.y, self.max_velocity.y))
        self.sprite.position = self.sprite.position + (self.velocity * tick.delta_time)
