from pathlib import Path

from pygame import Vector2

from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.components.render import RendererComponent
from justkeepswimming.components.sprite import SpriteComponent
from justkeepswimming.ecs import Component, Processor
from justkeepswimming.processors.render import RendererProcessor
from justkeepswimming.processors.sizing import RendererTransformConstraintProcessor
from justkeepswimming.processors.sprite import SpriteProcessor
from justkeepswimming.utilities.image import Image
from justkeepswimming.utilities.prefab import Prefab


class SpritePrefab(Prefab):
    components: list[Component] = [
        RendererComponent(),
        TransformComponent(
            position=Vector2(300, 300), size=Vector2(100, 100), anchor=Vector2(0.5, 0.5)
        ),
        SpriteComponent(Image(Path("assets/kitty.jpg"))),
    ]
    processors: list[type[Processor]] = [
        RendererProcessor,
        RendererTransformConstraintProcessor,
        SpriteProcessor,
    ]
