from components.sizing import ScreenSizeConstraint
from src.components.physics import Transform
from src.ecs import SceneContext, System
from src.modules.clock import TickContext
from src.utilities.context import GameContext

class SizeConstraint(System):
    reads = frozenset({ScreenSizeConstraint, Transform})
    writes = frozenset({Transform})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        window = engine_context.window
        for _, (transform, _) in scene_context.query(Transform, ScreenSizeConstraint):
            transform.size = window.size
        
