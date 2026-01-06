import asyncio
import enum
import logging
from asyncio import Task
from pathlib import Path

import pygame
from pygame import Rect, Surface, Vector2, image

from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.utilities.transform import Transform

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

    async def get_surface(self) -> Surface:
        if not self.loaded:
            await self.load()
        assert self._surface is not None
        return self._surface

    @property
    def loaded(self) -> bool:
        return self._surface is not None

    async def load(self) -> Surface:
        if self._surface and self.loaded:
            return self._surface
        await self.__load()
        assert self._surface is not None
        return self._surface

    async def __load(self) -> None:
        try:
            self._surface = image.load(self.path).convert_alpha()
        except FileNotFoundError as err:
            logger.warning(f"Failed to load {self.path}: Asset not found.")
            raise err
        self.transform = TransformComponent(
            position=Vector2(0, 0),
            rotation=0.0,
            size=Vector2(self._surface.get_size()),
            anchor=Vector2(0.5, 0.5),
        )
        logger.debug(
            f"Image loaded from {self.path} with size {self._surface.get_size()}"
        )


class Frame:
    def __init__(self, transform: Transform) -> None:
        self.logger = logging.getLogger("Frame")
        self.transform = transform

    async def slice(self, texture: Image) -> Surface:
        anchor_offset = self.transform.size.elementwise() * self.transform.anchor
        top_left = self.transform.position - anchor_offset

        region = (await texture.get_surface()).subsurface(
            Rect(top_left, self.transform.size)
        )

        if self.transform.rotation != 0:
            region = pygame.transform.rotate(region, -self.transform.rotation)

        return region
