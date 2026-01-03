from pygame import Color

from justkeepswimming.components.physics import Transform
from justkeepswimming.components.render import Camera, TextRenderer
from justkeepswimming.ecs import SceneContext, System
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.utilities.context import GameContext


BACKGROUND_COLOR: Color = Color(255, 0, 0)


class RenderSystem(System):
    reads = frozenset({Transform, Camera, TextRenderer})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        scene = scene_context.surface
        scene.fill(BACKGROUND_COLOR)
        
