import math
from pathlib import Path
from typing import Dict
from pygame import Vector2

from clock import Tick
from entities import Entity
from input import KeyBind, KeyCode, KeyMap
from sprites import AnimatedSprite, Animation, AnimationPriority, AnimationTrack, AnimationType

def lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolate from a to b by t (0..1)."""
    return a + (b - a) * t

class Player:
    """An object representing the player. Handles input, entity and rendering.
    """
    def __init__(self, keymap: KeyMap) -> None:
        self.sprite = AnimatedSprite(frame_size=Vector2(48, 48), path=Path("assets/spritesheet/turtle.png"))
        self.sprite.size = Vector2(100, 100)
        self.sprite.position = Vector2(300, 300)
        self.sprite.rotation = 100

        self.tracks: Dict[AnimationType, AnimationTrack] = {}
        self.tracks[AnimationType.Idle] = self.sprite.play(Animation(AnimationType.Idle, speed=1/10, loop=True), AnimationPriority.Low)

        self.entity = Entity(self.sprite)
        self.input_map: Dict[KeyBind, Vector2] = {
            keymap.bind("Move upwards", "Moves the player's character upwards", KeyCode.W): Vector2(0, -1),
            keymap.bind("Move left", "Moves the player's character to the left", KeyCode.A): Vector2(-1, 0),
            keymap.bind("Move downwards", "Moves the player's character downwards", KeyCode.S): Vector2(0, 1),
            keymap.bind("Move right", "Moves the player's character to the right", KeyCode.D): Vector2(1, 0)
        }

    async def update(self, tick: Tick) -> None:
        """Update the entity's wish direction, sprite rotation, and walking animation."""
        wish_direction = Vector2(0, 0)
        for key, force in self.input_map.items():
            if key.active:
                wish_direction += force

        is_moving = wish_direction.length_squared() > 0
        self.entity.wish_direction = wish_direction.normalize() if is_moving else Vector2(0, 0)

        if is_moving:
            self.sprite.mirrored = wish_direction.x < 0

            vertical_input = 0
            for key, force in self.input_map.items():
                if key.active:
                    vertical_input += force.y

            vertical_input = max(-1, min(1, vertical_input))
            max_angle = 180 * (math.pi / 180)
            target_rotation = -vertical_input * max_angle
            lerp_factor = 0.2
            self.sprite.rotation = lerp(self.sprite.rotation, target_rotation, lerp_factor)

        else:
            lerp_factor = 0.2
            self.sprite.rotation = lerp(self.sprite.rotation, 0, lerp_factor)
        
        walk_track = self.tracks.get(AnimationType.Walk)

        if is_moving:
            if not walk_track:
                walk_track = self.sprite.play(
                    Animation(AnimationType.Walk, speed=1 / 7.5, loop=True),
                    AnimationPriority.Medium,
                )
                self.tracks[AnimationType.Walk] = walk_track

            speed_base = 1 / 7.5
            speed_variation = (wish_direction.length() - 1) * (1 / 15)
            walk_track.animation.speed = speed_base + speed_variation

        else:
            if walk_track:
                await walk_track.cancel()
                self.tracks.pop(AnimationType.Walk)

