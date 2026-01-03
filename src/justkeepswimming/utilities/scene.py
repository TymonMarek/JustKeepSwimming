from logging import getLogger

from pygame import Event, Surface, Vector2

from justkeepswimming.scenes import SceneID
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.ecs.scheduler import SystemScheduler
from justkeepswimming.utilities.context import GameContext
from justkeepswimming.ecs import SceneContext
from justkeepswimming.utilities.signal import Signal

# Import for DAG visualizer
try:
    from justkeepswimming.utilities.dag_visualizer import (
        extract_graph_data_from_scheduler,
    )

    DAG_VISUALIZER_AVAILABLE = True
except ImportError:
    DAG_VISUALIZER_AVAILABLE = False


class Scene:
    def __init__(self, id: SceneID, dag_visualizer=None) -> None:
        self.id: SceneID = id
        self.logger = getLogger(__name__)
        self.context = SceneContext(surface=Surface(Vector2(960, 540)))
        self.scheduler = SystemScheduler()
        self.dag_visualizer = dag_visualizer
        self.on_load = Signal()
        self.on_enter = Signal[GameContext]()
        self.on_tick = Signal[TickContext, GameContext]()
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
        self, tick_context: TickContext, engine_context: GameContext
    ) -> None:
        await self.scheduler.process_tick(tick_context, self.context, engine_context)

        # Update DAG visualizer if available
        if self.dag_visualizer and DAG_VISUALIZER_AVAILABLE:
            try:
                graph_data = extract_graph_data_from_scheduler(self.scheduler)
                self.dag_visualizer.update_graph(graph_data)
            except Exception as e:
                self.logger.warning(f"Failed to update DAG visualizer: {e}")

    def __repr__(self) -> str:
        return self.id.name
