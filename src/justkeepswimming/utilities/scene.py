from logging import getLogger

from pygame import Event, Surface, Vector2

from justkeepswimming.ecs import SceneContext
from justkeepswimming.ecs.scheduler import ProcessorScheduler
from justkeepswimming.scenes import SceneID
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext
from justkeepswimming.utilities.signal import Signal

INTERNAL_RENDER_WINDOW_SIZE = Vector2(1920, 1080)


class Scene:
    def __init__(self, id: SceneID) -> None:
        self.id: SceneID = id
        self.logger = getLogger(__name__)
        self.context = SceneContext(surface=Surface(INTERNAL_RENDER_WINDOW_SIZE))
        self.scheduler = ProcessorScheduler()
        self.on_load = Signal()
        self.on_enter = Signal[EngineContext]()
        self.on_tick = Signal[TickContext, EngineContext]()
        self.on_exit = Signal()
        self.on_unload = Signal()
        self.on_exit.connect(self._handle_exit)
        self.on_tick.connect(self._process_systems)

    async def _handle_exit(self) -> None:
        self.context.maid.cleanup()

    async def _on_window_resize(self, event: Event) -> None:
        self.context.surface = Surface(Vector2(event.w, event.h))
        self.logger.debug(f"Scene {self.id} resized to Vector2({event.w}, {event.h})")

    async def _process_systems(
        self, tick_context: TickContext, engine_context: EngineContext
    ) -> None:
        await self.scheduler.process_tick(tick_context, self.context, engine_context)

    def __repr__(self) -> str:
        return self.id.name
