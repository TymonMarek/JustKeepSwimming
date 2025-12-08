from dataclasses import dataclass, field
from typing import Any, DefaultDict, List, Optional, overload, TypeVar
from enum import Enum, auto
from functools import cache
from pathlib import Path
import importlib
import sys

from window import Window
from clock import Tick
from emitter import Emitter
from entities import Entity
from player import Player
from sprites import Sprite

class SceneType(Enum):
    Unassigned = auto()
    Menu = auto()
    Level = auto()

SCENE_DIR = Path("src/scenes")

class ParseError(Exception):
    pass

@dataclass
class SceneContext():
    switch: Emitter[str] = field(default_factory=lambda: Emitter[str]())
    sprites: DefaultDict[int, List[Sprite]] = field(default_factory=lambda: DefaultDict(list))
    entities: List[Entity] = field(default_factory=list[Entity])

T = TypeVar("T")

class Scene:
    def __init__(self, name: str, scene_type: Optional[SceneType]) -> None:
        self.name = name
        self.type: Optional[SceneType] = scene_type

        self.context = SceneContext()
        self.unloading = Emitter()
        self.loaded = Emitter()

    async def update(self, tick: Tick, window: Window, player: Player) -> None:
        if self.type in [SceneType.Level, SceneType.Menu]:
            for entity in self.context.entities:
                entity.update(tick)

            for z_index in sorted(self.context.sprites.keys()):
                for sprite in self.context.sprites[z_index]:
                    await sprite.update(tick)
                    sprite.draw(window.surface)

        if self.type == SceneType.Level:
            await player.update(tick)
            player.entity.update(tick)
            await player.sprite.update(tick)
            player.sprite.draw(window.surface)

    @overload
    def add(self, target: Sprite) -> Sprite: ...

    @overload
    def add(self, target: Entity) -> Entity: ...

    def add(self, target: T) -> T:
        if isinstance(target, Sprite):
            self._add_sprite(target)
        elif isinstance(target, Entity):
            self._add_entity(target)
        return target

    def _add_sprite(self, sprite: Sprite) -> None:
        self.context.sprites[sprite.z_index].append(sprite)

    def _add_entity(self, entity: Entity) -> None:
        self.context.entities.append(entity)

    @staticmethod
    @cache
    def resolve(name: str) -> "Scene":
        # Make sure the file exists
        scene_path = SCENE_DIR / f"{name}.py"
        if not scene_path.exists():
            raise FileNotFoundError(f"Scene not found: {scene_path}")

        # Import the Python module
        scene_data = importlib.import_module(f"scenes.{name}")

        # Look for exported scene object
        exported_scene: Optional[Any] = getattr(scene_data, "export", None)
        if not isinstance(exported_scene, Scene):
            raise ParseError(f"Not a valid scene: {scene_path}")

        return exported_scene

    def __repr__(self) -> str:
        return (
            f"<Scene name={self.name!r} "
            f"type={self.type} "
            f"sprites={sum(len(s) for s in self.context.sprites.values())} "
            f"entities={len(self.context.entities)} "
            f"memory={sys.getsizeof(self) / (1024 * 1024):.2f} MB>"
        )
