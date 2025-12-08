from enum import Enum
from pathlib import Path
from typing import DefaultDict, List, Dict, Optional

from pygame import Surface, Vector2
import pygame

from clock import Tick
from emitter import Emitter

layers: DefaultDict[int, List["Sprite"]] = DefaultDict(list)
""" A dictionary mapping z-index to a list of sprites at that z-index
"""

pygame.display.init()

class Sprite:
    """An object that will be drawn to the screen. The contents of `Sprite.surface` will be drawn at `Sprite.position` on the target surface provided in `Sprite.draw()`.
    """
    def __init__(self) -> None:
        self._size = Vector2(0, 0)
        self.rotation = 0.0
        self.mirrored = False
        self.position = Vector2(0, 0)
        self.surface = Surface(self.size)
        self._z_index: int = 0
        self.__post_init__()

    def __post_init__(self) -> None:
        layer = layers[self.z_index]
        layer.append(self)

    async def update(self, tick: Tick):
        """A function that fires at every tick. Should only be used when the sprite is animated or modified.

        Args:
            tick (`Tick`): The current tick information.
        """
        ...

    @property
    def z_index(self) -> int:
        return self._z_index
    
    @z_index.setter
    def z_index(self, new_z_index: int):
        if self._z_index == new_z_index:
            return 
        current_layer = layers[self._z_index]
        if self in current_layer:
            current_layer.remove(self)
        self._z_index = new_z_index   
        new_layer = layers[new_z_index]
        new_layer.append(self)

    @property
    def size(self) -> Vector2:
        return self._size
    
    @size.setter
    def size(self, new_size: Vector2):
        if new_size == self._size:
            return
        self._size = new_size
        self.surface = pygame.transform.scale(self.surface, self._size)

    def draw(self, target: Surface) -> None:
        """Draws the contents of `Sprite.surface` to the `target` surface at `Sprite.position`.

        Args:
            target (`pygame.Surface`): The surface to draw to.
        """
        final_image = pygame.transform.rotate(self.surface, self.rotation)
        if self.mirrored:
            final_image = pygame.transform.flip(final_image, True, False)
        target.blit(final_image, self.position)

    @staticmethod
    def from_path(path: Path) -> "Sprite":
        sprite = Sprite()
        try:
            sprite.surface = pygame.image.load(path).convert_alpha()
            sprite.size = Vector2(sprite.surface.get_size())
        except FileNotFoundError:
            print(f"Failed to load {path}, file not found.")
        return sprite


class AnimationType(Enum):
    Idle = 0
    Walk = 1
    Attack = 2
    Hurt = 3
    Death = 4


class AnimationPriority(Enum):
    Low = 0
    Medium = 1
    High = 2
    Immediate = 3


class Animation():
    def __init__(self, animation_type: AnimationType, speed: float = 1/3, loop: bool = False) -> None: 
        self.type: AnimationType = animation_type
        self.loop: bool = loop 
        self.speed: float = speed

    def __repr__(self) -> str:
        return f"Animation({self.type=}, {self.loop=})"


class AnimationTrack():
    def __init__(self, track_queue: "AnimationTrackQueue", animation: Animation, priority: AnimationPriority = AnimationPriority.Low) -> None:
        self._track_queue = track_queue
        self.animation = animation
        self.priority = priority
        self.current_frame_index = 0
        self.playing: bool = False
        self.interrupted = Emitter()
        self.started = Emitter()
        self.looped = Emitter()
        self.finished = Emitter()
        self.cancelled = Emitter()
        self.frame_time_accumulator: float = 0.0

    async def cancel(self) -> None:
        self._track_queue.remove(self)
        await self.interrupted.emit()
        await self.cancelled.emit()

    def __repr__(self) -> str:
        return f"AnimationTrack({self.animation=}, {self.priority=}, {self.current_frame_index=}, {self.playing=})"


def is_surface_empty(surface: Surface) -> bool:
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if surface.get_at((x, y)).a != 0:
                return False
    return True


class AnimationTrackQueue():
    def __init__(self) -> None:
        self.elements: List[AnimationTrack] = []
        
    def empty(self) -> bool:
        return len(self.elements) == 0
    
    def peek(self) -> Optional[AnimationTrack]:
        return self.elements[0] if self.elements else None
    
    def remove(self, track: AnimationTrack) -> None:
        self.elements.remove(track)

    def put(self, track: AnimationTrack) -> None:
        self.elements.append(track)
        self.elements.sort(key=lambda track: track.priority.value, reverse=True)

    def __repr__(self) -> str:
        items = ",\n  ".join(repr(track) for track in self.elements)
        return f"AnimationTrackQueue([\n  {items}\n])"


class AnimatedSprite(Sprite):
    def __init__(self, frame_size: Vector2, path: Optional[Path],) -> None:
        super().__init__()
        self.track_queue: AnimationTrackQueue = AnimationTrackQueue()
        self.frames: Dict[AnimationType, List[Surface]] = {}
        self.current_track: Optional[AnimationTrack] = None
        self.frame_size = frame_size
        self.path: Optional[Path] = path
        if path:
            self.load(path, self.frame_size)

    def load(self, path: Path, frame_size: Vector2) -> None:
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sheet_width, sheet_height = sheet.get_size()
            
            for y in range(0, sheet_height, int(frame_size.y)):
                for x in range(0, sheet_width, int(frame_size.x)):
                    frame = sheet.subsurface(pygame.Rect(x, y, frame_size.x, frame_size.y))
                    if is_surface_empty(frame):
                        continue
                    animation_type = AnimationType(y // int(frame_size.y))
                    if animation_type not in self.frames:
                        self.frames[animation_type] = []
                    self.frames[animation_type].append(frame)
        except FileNotFoundError:
            print(f"Failed to load {path}, file not found.")

    async def update(self, tick: Tick):
        await super().update(tick)

        track = self.track_queue.peek()
        if not track:
            return

        if self.current_track != track:
            await self._switch_to_new_track(track)

        await self._advance_track_frame(track, tick.delta_time)

    async def _switch_to_new_track(self, new_track: AnimationTrack):
        if self.current_track:
            self.current_track.playing = False
            await self.current_track.interrupted.emit()

        self.current_track = new_track

        new_track.current_frame_index = 0
        new_track.frame_time_accumulator = 0.0

        new_track.playing = True
        await new_track.started.emit()

    async def _advance_track_frame(self, track: AnimationTrack, delta_time: float):
        frames = self.frames.get(track.animation.type, [])
        if not frames:
            return

        seconds_per_frame = track.animation.speed        
        track.frame_time_accumulator += delta_time

        if track.frame_time_accumulator < seconds_per_frame:
            self.surface = frames[track.current_frame_index]
            return

        steps = int(track.frame_time_accumulator / seconds_per_frame)
        track.frame_time_accumulator -= steps * seconds_per_frame

        total_frames = len(frames)
        new_index = track.current_frame_index + steps

        if track.animation.loop:
            if new_index >= total_frames:
                await track.looped.emit()

            track.current_frame_index = new_index % total_frames
        else:
            if new_index >= total_frames:
                track.current_frame_index = total_frames - 1
                track.playing = False
                await track.finished.emit()
                self.track_queue.remove(track)
            else:
                track.current_frame_index = new_index

        self.surface = frames[track.current_frame_index]

    def play(self, animation: Animation, priority: AnimationPriority = AnimationPriority.Low) -> AnimationTrack:
        track = AnimationTrack(self.track_queue, animation, priority)
        self.track_queue.put(track)
        return track
