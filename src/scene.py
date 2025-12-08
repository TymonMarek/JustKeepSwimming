from dataclasses import dataclass, field
from typing import Any, DefaultDict, List, Optional, overload
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
    """A context manager that exposes scene switching controls within a scene file. The manager will be available within scene files as the variable `context`.
    """
    switch: Emitter[str] = field(default_factory=lambda: Emitter[str]())
    """A scene switch emitter. Emitting on this emitter will request the stage to load a different scene.

    Raises:
        FileNotFoundError: Raised when the requested scene file does not exist.
        ParseError: Raised when the scene file cannot be parsed correctly.
    """
    sprites: DefaultDict[int, List[Sprite]] = field(default_factory=lambda: DefaultDict(list))
    """A dictionary mapping z-index values to lists of sprites in the scene.
    """
    entities: List[Entity] = field(default_factory=list[Entity])
    """A list of entities in the scene.
    """


class Scene:
    """A class representing a scene in the game. Scenes are containers for sprites and entities, and manage their updates and rendering.
    """
    def __init__(self, name: str, scene_type: Optional[SceneType]) -> None:
        self.name = name
        self.type: Optional[SceneType] = scene_type
        """A SceneType enum value representing the type of the scene. 

            `SceneType.Unassigned`: A scene that does not do anything by default.\n
            `SceneType.Menu`: A menu scene without player or level logic.\n
            `SceneType.Level`: A playable level with player and entities.\n
        """

        self.context = SceneContext()
        """The context manager that exposes scene data and switching controls within the scene.
        """
        self.unloading = Emitter()
        """Emitted when the scene is unloading.
        """
        self.loaded = Emitter()
        """Emitted when the scene has finished loading.
        """

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

    def add[T](self, target: T) -> T:
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
        if not (scene_path := SCENE_DIR / f"{name}.py").exists():
            raise FileNotFoundError(f"Scene not found: {name}")
        scene_path = SCENE_DIR / f"{name}.py"
        scene_data = importlib.import_module(f"scenes.{name}", package=__package__)

        exported_scene: Optional[Any] = getattr(scene_data, "export", None)
        if not exported_scene or not isinstance(exported_scene, Scene):
            raise ParseError(f"Scene could not be parsed: {scene_path}")

        return exported_scene
    
    def __repr__(self) -> str:
        return (
            f"<Scene name={self.name!r} "
            f"type={self.type} "
            f"sprites={sum(len(s) for s in self.context.sprites.values())} "
            f"entities={len(self.context.entities)} "
            f"memory={sys.getsizeof(self) / (1024 * 1024):.2f} MB>"
        )