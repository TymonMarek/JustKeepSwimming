import asyncio
import enum
import logging
from asyncio import Task
from pathlib import Path

import pygame
from pygame import Rect, Surface, Vector2, image

from justkeepswimming.components.physics import TransformComponent

logger = logging.getLogger(__name__)


class ImageLoadingStrategy(enum.Enum):
    LAZY = enum.auto()
    IMMEDIATE = enum.auto()


class Image:
    _cache: dict[Path, "Image"] = {}

    def __new__(
        cls,
        path: Path,
        strategy: ImageLoadingStrategy = ImageLoadingStrategy.LAZY,
    ):
        if path in cls._cache:
            logger.debug(f"Cache hit: {path}")
            return cls._cache[path]

        logger.debug(f"Cache miss: {path}")

        instance = super().__new__(cls)
        cls._cache[path] = instance
        return instance

    def __deepcopy__(self, memo: dict[int, object]) -> "Image":
        return self

    def __init__(
        self, path: Path, strategy: ImageLoadingStrategy = ImageLoadingStrategy.LAZY
    ) -> None:
        self.path = path
        self._surface: Surface | None = None
        self.transform: TransformComponent | None = None
        self._load_task: Task[None] | None = None

        if strategy == ImageLoadingStrategy.IMMEDIATE:
            logger.debug(f"Immediately loading image from {path}")
            self._load_task = asyncio.create_task(self.__load())
        logger.debug(f"{path} will be lazily loaded when accessed")

    @property
    def surface(self) -> Surface:
        if not self.loaded:
            logger.debug(
                f"Image {self.path} was requested but not loaded yet, lazily loading it now..."
            )
            self._load_task = asyncio.create_task(self.__load())
            return Surface((0, 0))
        assert self._surface is not None
        return self._surface

    @property
    def loaded(self) -> bool:
        return self._surface is not None

    async def load(self) -> Surface:
        if self._surface and self.loaded:
            return self._surface

        if self._load_task is None:
            self._load_task = asyncio.create_task(self.__load())

        await self._load_task
        assert self._surface is not None
        return self._surface

    async def __load(self) -> None:
        try:
            self._surface = image.load(self.path).convert_alpha()
        except FileNotFoundError:
            logger.warning(f"Failed to load {self.path}: Asset not found.")
            self._surface = Surface((0, 0))
        self.transform = TransformComponent(
            position=Vector2(0, 0),
            rotation=0.0,
            size=Vector2(self._surface.get_size()),
            anchor=Vector2(0.5, 0.5),
        )
        logger.debug(
            f"Image loaded from {self.path} with size {self._surface.get_size()}"
        )


class ImageRegion:
    def __init__(self, transform: TransformComponent) -> None:
        self.transform = transform

    def slice(self, texture: Image) -> Surface:
        if not texture.surface or not texture.loaded:
            return Surface((0, 0))

        anchor_offset = self.transform.size.elementwise() * self.transform.anchor
        top_left = self.transform.position - anchor_offset

        region = Surface(self.transform.size, flags=texture.surface.get_flags())
        region.blit(
            source=texture.surface,
            dest=Vector2(0, 0),
            area=Rect(top_left, self.transform.size),
        )

        if self.transform.rotation != 0:
            region = pygame.transform.rotate(region, -self.transform.rotation)

        return region


class Keyframe:
    def __init__(self, timestamp: float, region: ImageRegion) -> None:
        self.timestamp: float = timestamp
        self.region: ImageRegion = region


class AnimationPriority(enum.Enum):
    RESERVED = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


class KeyframeSequence:
    def __init__(self, keyframes: list[Keyframe]) -> None:
        self.keyframes: list[Keyframe] = sorted(
            keyframes, key=lambda keyframe: keyframe.timestamp
        )
        self.duration: float = max(keyframe.timestamp for keyframe in self.keyframes)


class Animation:
    def __init__(
        self, texture: Image, sequence: KeyframeSequence, priority: AnimationPriority
    ) -> None:
        self.texture: Image = texture
        self.sequence: KeyframeSequence = sequence
        self.priority: AnimationPriority = priority
        self.looped: bool = True
        self.speed: float = 1.0


class AnimationTrack:
    def __init__(self, animation: Animation) -> None:
        self.animation: Animation = animation
        self.priority: AnimationPriority = animation.priority
        self.looped: bool = animation.looped
        self.speed: float = animation.speed
        self.frames: list[Surface] = []
        self.time: float = 0.0

    async def load(self) -> None:
        if not self.animation.texture.loaded:
            await self.animation.texture.load()

        for keyframe in self.animation.sequence.keyframes:
            self.frames.append(keyframe.region.slice(self.animation.texture))


class Animator:
    def __init__(self) -> None:
        self.tracks: list[AnimationTrack] = []

    async def load(self, animation: Animation) -> AnimationTrack:
        track = AnimationTrack(animation)
        await track.load()
        self.tracks.append(track)
        return track
