from pathlib import Path
from pygame import Vector2

from justkeepswimming.components.physics import Transform
from justkeepswimming.components.render import Renderer
from justkeepswimming.components.sprite import SpriteComponent
from justkeepswimming.ecs import Component, System
from justkeepswimming.systems.render import RenderSystem
from justkeepswimming.systems.sizing import RendererTransformConstraintSystem
from justkeepswimming.systems.sprite import SpriteSystem
from justkeepswimming.utilities.prefab import Prefab
from justkeepswimming.utilities.image import Image

class SpritePrefab(Prefab):
    components: list[Component] = [
        Renderer(),
        Transform(
            position=Vector2(300, 300), size=Vector2(100, 100), anchor=Vector2(0.5, 0.5)
        ),
        SpriteComponent(Image(Path("assets/kitty.jpg"))),
    ]
    systems: list[type[System]] = [
        RenderSystem,
        RendererTransformConstraintSystem,
        SpriteSystem
    ]
